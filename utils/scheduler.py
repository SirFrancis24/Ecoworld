from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from flask import current_app
import logging
import random
from datetime import datetime, timedelta

from app import db
from models import Nation, Resource, MarketItem, Trade, Technology, Military, User, SpyMission, DeployedSpy
from utils.game_logic import update_resources, calculate_rankings
from utils.technology_handler import update_research_progress
from utils.advanced_espionage import check_active_missions, update_spy_cover_and_intel
from utils.news_generator import generate_daily_news

# Configure logger
logger = logging.getLogger(__name__)

def update_research_progress_wrapper():
    """Wrapper function to call update_research_progress with app context"""
    try:
        from flask import current_app as app
        with app.app_context():
            logger.info("Updating research progress for all nations.")
            try:
                result = update_research_progress()
                logger.info(f"Research progress updated: {result['updated_count']} updated, {result['completed_count']} completed.")
            except Exception as e:
                logger.error(f"Error updating research progress: {str(e)}")
    except RuntimeError:
        logger.error("Failed to get application context for research progress update.")

def check_spy_missions_wrapper():
    """Wrapper function to check espionage missions with app context"""
    try:
        from flask import current_app as app
        with app.app_context():
            logger.info("Checking for completed spy missions.")
            try:
                result = check_active_missions()
                logger.info(f"Processed {result.get('total_completed', 0)} completed spy missions.")
            except Exception as e:
                logger.error(f"Error checking spy missions: {str(e)}")
    except RuntimeError:
        logger.error("Failed to get application context for spy missions check.")

def update_spy_status_wrapper():
    """Wrapper function to update spy status with app context"""
    try:
        from flask import current_app as app
        with app.app_context():
            logger.info("Updating spy cover and intel levels.")
            try:
                result = update_spy_cover_and_intel()
                logger.info(f"Updated {result.get('spies_updated', 0)} active spies.")
            except Exception as e:
                logger.error(f"Error updating spy status: {str(e)}")
    except RuntimeError:
        logger.error("Failed to get application context for spy status update.")

def generate_daily_news_wrapper():
    """Wrapper function to generate daily news with app context"""
    try:
        from flask import current_app as app
        with app.app_context():
            logger.info("Generating daily news articles.")
            try:
                articles_created = generate_daily_news()
                logger.info(f"Generated {articles_created} news articles.")
            except Exception as e:
                logger.error(f"Error generating daily news: {str(e)}")
    except RuntimeError:
        logger.error("Failed to get application context for news generation.")

def init_scheduler(app):
    """Initialize the background scheduler for periodic tasks"""
    scheduler = BackgroundScheduler()
    
    # Add scheduled tasks
    
    # Update resources for all nations every hour
    scheduler.add_job(
        func=update_all_resources,
        trigger=IntervalTrigger(hours=1),
        id='update_resources_job',
        name='Update resources for all nations',
        replace_existing=True
    )
    
    # Update rankings every 6 hours
    scheduler.add_job(
        func=update_rankings,
        trigger=IntervalTrigger(hours=6),
        id='update_rankings_job',
        name='Update nation rankings',
        replace_existing=True
    )
    
    # Clean up expired market listings every hour
    scheduler.add_job(
        func=cleanup_market,
        trigger=IntervalTrigger(hours=1),
        id='cleanup_market_job',
        name='Clean up expired market listings',
        replace_existing=True
    )
    
    # Update research progress every minute to make progress bars accurate
    scheduler.add_job(
        func=update_research_progress_wrapper,
        trigger=IntervalTrigger(minutes=1),
        id='update_research_progress_job',
        name='Update research progress for all nations',
        replace_existing=True
    )
    
    # Check for completed spy missions every 15 minutes
    scheduler.add_job(
        func=check_spy_missions_wrapper,
        trigger=IntervalTrigger(minutes=15),
        id='check_spy_missions_job',
        name='Check completed spy missions',
        replace_existing=True
    )
    
    # Update spy cover strength and intel level every hour
    scheduler.add_job(
        func=update_spy_status_wrapper,
        trigger=IntervalTrigger(hours=1),
        id='update_spy_status_job',
        name='Update spy status',
        replace_existing=True
    )
    
    # Bot market activity every 3 hours
    scheduler.add_job(
        func=bot_market_activity,
        trigger=IntervalTrigger(hours=3),
        id='bot_market_activity_job',
        name='Bot market activity',
        replace_existing=True
    )
    
    # Generate daily news
    scheduler.add_job(
        func=generate_daily_news_wrapper,
        trigger=IntervalTrigger(hours=24),
        id='generate_daily_news_job',
        name='Generate daily news',
        replace_existing=True
    )
    
    # Start the scheduler
    scheduler.start()
    logger.info("Scheduler started.")
    
    # Shut down the scheduler when the app shuts down
    @app.teardown_appcontext
    def shutdown_scheduler(exception=None):
        try:
            if scheduler.running:
                scheduler.shutdown(wait=False)
                logger.info("Scheduler shut down successfully.")
        except Exception as e:
            logger.error(f"Error shutting down scheduler: {str(e)}")

def update_all_resources():
    """Update resources for all nations"""
    with current_app.app_context():
        logger.info("Updating resources for all nations.")
        nations = Nation.query.all()
        for nation in nations:
            try:
                update_resources(nation)
            except Exception as e:
                logger.error(f"Error updating resources for nation {nation.id}: {str(e)}")
        
        logger.info(f"Resources updated for {len(nations)} nations.")

def update_rankings():
    """Update rankings for all nations"""
    with current_app.app_context():
        logger.info("Updating nation rankings.")
        try:
            calculate_rankings()
            logger.info("Rankings updated successfully.")
        except Exception as e:
            logger.error(f"Error updating rankings: {str(e)}")

def cleanup_market():
    """Clean up expired market listings"""
    with current_app.app_context():
        logger.info("Cleaning up expired market listings.")
        now = datetime.utcnow()
        
        try:
            # Find expired listings
            expired_listings = MarketItem.query.filter(
                MarketItem.expires_at < now,
                MarketItem.is_active == True
            ).all()
            
            logger.info(f"Found {len(expired_listings)} expired listings.")
            
            for listing in expired_listings:
                # Return resources to seller
                seller_resources = Resource.query.filter_by(nation_id=listing.seller_id).first()
                if seller_resources:
                    # Add the resources back to the seller's inventory
                    current_amount = getattr(seller_resources, listing.resource_type)
                    setattr(seller_resources, listing.resource_type, current_amount + listing.quantity)
                
                # Mark listing as inactive
                listing.is_active = False
            
            db.session.commit()
            logger.info("Expired listings processed successfully.")
        except Exception as e:
            logger.error(f"Error cleaning up market listings: {str(e)}")
            db.session.rollback()

def bot_market_activity():
    """AI bots interact with the market - create listings and buy underpriced resources"""
    with current_app.app_context():
        logger.info("Running bot market activity.")
        now = datetime.utcnow()
        
        try:
            # Get AI-controlled nations (those not linked to users)
            ai_nations = Nation.query.filter(
                ~Nation.user_id.in_(db.session.query(User.id))
            ).all()
            
            if not ai_nations:
                logger.info("No AI nations found.")
                return
                
            logger.info(f"Found {len(ai_nations)} AI nations for market activity.")
            
            # Current market average prices
            avg_prices = {}
            for resource_type in ['raw_materials', 'food', 'energy']:
                trades = Trade.query.filter_by(resource_type=resource_type).order_by(
                    Trade.trade_date.desc()).limit(10).all()
                
                if trades:
                    avg_price = sum(trade.price_per_unit for trade in trades) / len(trades)
                    # Add 10% variance
                    avg_prices[resource_type] = avg_price * (0.9 + (random.random() * 0.2))
                else:
                    # Fallback prices if no trades exist
                    default_prices = {
                        'raw_materials': 10.0,
                        'food': 15.0,
                        'energy': 20.0
                    }
                    avg_prices[resource_type] = default_prices[resource_type]
            
            # Some AI nations will create listings
            for nation in random.sample(ai_nations, min(3, len(ai_nations))):
                resources = Resource.query.filter_by(nation_id=nation.id).first()
                if not resources:
                    continue
                    
                # Choose a random resource to sell
                resource_type = random.choice(['raw_materials', 'food', 'energy'])
                current_amount = getattr(resources, resource_type, 0)
                
                # Only sell if they have enough (at least 20% of production rate)
                min_amount = getattr(resources, f"{resource_type}_production") * 0.2
                if current_amount > min_amount:
                    # Sell between 10-30% of current amount
                    quantity = current_amount * (0.1 + (random.random() * 0.2))
                    # Random price around average (+/- 15%)
                    price_per_unit = avg_prices[resource_type] * (0.85 + (random.random() * 0.3))
                    
                    # Create listing
                    listing = MarketItem(
                        seller_id=nation.id,
                        resource_type=resource_type,
                        quantity=quantity,
                        price_per_unit=price_per_unit,
                        total_price=quantity * price_per_unit,
                        created_at=now,
                        expires_at=now + timedelta(days=1),
                        is_active=True
                    )
                    
                    # Deduct resources
                    setattr(resources, resource_type, current_amount - quantity)
                    
                    db.session.add(listing)
                    logger.info(f"AI nation {nation.name} created listing for {quantity} {resource_type}")
            
            # Some AI nations will buy underpriced listings
            active_listings = MarketItem.query.filter_by(is_active=True).all()
            for nation in random.sample(ai_nations, min(2, len(ai_nations))):
                resources = Resource.query.filter_by(nation_id=nation.id).first()
                if not resources or resources.currency < 1000:
                    continue
                
                # Look for good deals (15% or more below average price)
                good_deals = [
                    listing for listing in active_listings
                    if (listing.seller_id != nation.id and  # Don't buy own listings
                        listing.price_per_unit < avg_prices[listing.resource_type] * 0.85 and
                        listing.total_price < resources.currency * 0.5)  # Don't spend more than 50% of currency
                ]
                
                if good_deals:
                    # Buy a random good deal
                    listing = random.choice(good_deals)
                    seller_resources = Resource.query.filter_by(nation_id=listing.seller_id).first()
                    
                    if seller_resources:
                        # Complete the transaction
                        # Deduct currency from buyer
                        resources.currency -= listing.total_price
                        
                        # Add currency to seller
                        seller_resources.currency += listing.total_price
                        
                        # Add resources to buyer
                        current_amount = getattr(resources, listing.resource_type)
                        setattr(resources, listing.resource_type, current_amount + listing.quantity)
                        
                        # Mark listing as inactive
                        listing.is_active = False
                        
                        # Create trade record
                        trade = Trade(
                            seller_id=listing.seller_id,
                            buyer_id=nation.id,
                            market_item_id=listing.id,
                            resource_type=listing.resource_type,
                            quantity=listing.quantity,
                            price_per_unit=listing.price_per_unit,
                            total_price=listing.total_price,
                            trade_date=now
                        )
                        
                        db.session.add(trade)
                        logger.info(f"AI nation {nation.name} purchased {listing.quantity} {listing.resource_type}")
            
            db.session.commit()
            logger.info("Bot market activity completed successfully.")
        except Exception as e:
            logger.error(f"Error during bot market activity: {str(e)}")
            db.session.rollback()
