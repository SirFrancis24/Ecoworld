from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, current_app
from flask_login import current_user
from app import db
from models import Nation, Resource, MarketItem, Trade
from datetime import datetime, timedelta
from utils.auth_helpers import easy_login_required

market = Blueprint('market', __name__)

@market.route('/market')
@easy_login_required
def market_view():
    # Get current user's nation
    nation = Nation.query.filter_by(user_id=current_user.id).first()
    resources = Resource.query.filter_by(nation_id=nation.id).first()
    
    # Get active market listings
    active_listings = MarketItem.query.filter_by(is_active=True).all()
    
    # Get market history for this nation
    selling_history = Trade.query.filter_by(seller_id=nation.id).order_by(Trade.trade_date.desc()).limit(10).all()
    buying_history = Trade.query.filter_by(buyer_id=nation.id).order_by(Trade.trade_date.desc()).limit(10).all()
    
    return render_template('market.html',
                          nation=nation,
                          resources=resources,
                          active_listings=active_listings,
                          selling_history=selling_history,
                          buying_history=buying_history)

@market.route('/market/create', methods=['POST'])
@easy_login_required
def create_listing():
    nation = Nation.query.filter_by(user_id=current_user.id).first()
    resources = Resource.query.filter_by(nation_id=nation.id).first()
    
    resource_type = request.form.get('resource_type')
    quantity = float(request.form.get('quantity', 0))
    price_per_unit = float(request.form.get('price_per_unit', 0))
    
    # Validate input
    if quantity <= 0:
        flash('Quantity must be greater than zero.', 'danger')
        return redirect(url_for('market.market_view'))
    
    if price_per_unit <= 0:
        flash('Price must be greater than zero.', 'danger')
        return redirect(url_for('market.market_view'))
    
    # Check if the nation has enough resources
    current_amount = getattr(resources, resource_type, 0)
    if current_amount < quantity:
        flash(f'Not enough {resource_type} available.', 'danger')
        return redirect(url_for('market.market_view'))
    
    # Create market listing
    total_price = quantity * price_per_unit
    
    listing = MarketItem(
        seller_id=nation.id,
        resource_type=resource_type,
        quantity=quantity,
        price_per_unit=price_per_unit,
        total_price=total_price,
        created_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(days=1),
        is_active=True
    )
    
    # Deduct the resources from the nation
    setattr(resources, resource_type, current_amount - quantity)
    
    try:
        db.session.add(listing)
        db.session.commit()
        flash(f'Successfully listed {quantity} {resource_type} on the market.', 'success')
    except Exception as e:
        db.session.rollback()
        # Log the error
        current_app.logger.error(f"Error creating market listing: {str(e)}")
        flash(f'Error creating market listing. Please try again.', 'danger')
    
    return redirect(url_for('market.market_view'))

@market.route('/market/buy/<int:listing_id>', methods=['POST'])
@easy_login_required
def buy_listing(listing_id):
    # Get the market listing
    listing = MarketItem.query.get_or_404(listing_id)
    
    # Make sure the listing is active
    if not listing.is_active:
        flash('This listing is no longer active.', 'danger')
        return redirect(url_for('market.market_view'))
    
    # Get the buyer's nation
    buyer_nation = Nation.query.filter_by(user_id=current_user.id).first()
    
    # Make sure the buyer is not the seller
    if buyer_nation.id == listing.seller_id:
        flash('You cannot buy your own listing.', 'danger')
        return redirect(url_for('market.market_view'))
    
    # Check if the buyer has enough currency
    buyer_resources = Resource.query.filter_by(nation_id=buyer_nation.id).first()
    if buyer_resources.currency < listing.total_price:
        flash('Not enough currency to complete this purchase.', 'danger')
        return redirect(url_for('market.market_view'))
    
    # Get the seller's resources
    seller_resources = Resource.query.filter_by(nation_id=listing.seller_id).first()
    
    # Execute the trade
    try:
        # Deduct currency from buyer
        buyer_resources.currency -= listing.total_price
        
        # Add currency to seller
        seller_resources.currency += listing.total_price
        
        # Add resources to buyer
        current_amount = getattr(buyer_resources, listing.resource_type)
        setattr(buyer_resources, listing.resource_type, current_amount + listing.quantity)
        
        # Mark the listing as inactive
        listing.is_active = False
        
        # Create a trade record
        trade = Trade(
            seller_id=listing.seller_id,
            buyer_id=buyer_nation.id,
            market_item_id=listing.id,
            resource_type=listing.resource_type,
            quantity=listing.quantity,
            price_per_unit=listing.price_per_unit,
            total_price=listing.total_price,
            trade_date=datetime.utcnow()
        )
        
        db.session.add(trade)
        db.session.commit()
        
        flash(f'Successfully purchased {listing.quantity} {listing.resource_type}.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error processing purchase: {str(e)}', 'danger')
    
    return redirect(url_for('market.market_view'))

@market.route('/market/cancel/<int:listing_id>', methods=['POST'])
@easy_login_required
def cancel_listing(listing_id):
    # Get the market listing
    listing = MarketItem.query.get_or_404(listing_id)
    
    # Make sure the user owns this listing
    nation = Nation.query.filter_by(user_id=current_user.id).first()
    if listing.seller_id != nation.id:
        flash('You do not own this listing.', 'danger')
        return redirect(url_for('market.market_view'))
    
    # Make sure the listing is still active
    if not listing.is_active:
        flash('This listing is no longer active.', 'danger')
        return redirect(url_for('market.market_view'))
    
    # Get the resources
    resources = Resource.query.filter_by(nation_id=nation.id).first()
    
    # Return the resources to the seller
    current_amount = getattr(resources, listing.resource_type)
    setattr(resources, listing.resource_type, current_amount + listing.quantity)
    
    # Mark the listing as inactive
    listing.is_active = False
    
    try:
        db.session.commit()
        flash(f'Listing cancelled. {listing.quantity} {listing.resource_type} returned to your inventory.', 'success')
    except Exception as e:
        db.session.rollback()
        # Log the error
        current_app.logger.error(f"Error cancelling market listing: {str(e)}")
        flash(f'Error cancelling listing. Please try again.', 'danger')
    
    return redirect(url_for('market.market_view'))

@market.route('/market/prices')
@easy_login_required
def market_prices():
    """Get recent market prices for charting"""
    
    # Get the price history from completed trades
    raw_materials_prices = Trade.query.filter_by(resource_type='raw_materials').order_by(Trade.trade_date.desc()).limit(20).all()
    food_prices = Trade.query.filter_by(resource_type='food').order_by(Trade.trade_date.desc()).limit(20).all()
    energy_prices = Trade.query.filter_by(resource_type='energy').order_by(Trade.trade_date.desc()).limit(20).all()
    
    # Format the data for the chart
    price_data = {
        'raw_materials': [{'date': trade.trade_date.strftime('%Y-%m-%d %H:%M'), 'price': trade.price_per_unit} for trade in raw_materials_prices],
        'food': [{'date': trade.trade_date.strftime('%Y-%m-%d %H:%M'), 'price': trade.price_per_unit} for trade in food_prices],
        'energy': [{'date': trade.trade_date.strftime('%Y-%m-%d %H:%M'), 'price': trade.price_per_unit} for trade in energy_prices]
    }
    
    return jsonify(price_data)