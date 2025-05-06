from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import current_user
from app import db
from models import Nation, Resource, Technology, Military, MarketItem, Trade, War, Alliance, NewsArticle
from datetime import datetime
from utils.game_logic import update_resources, calculate_rankings
from utils.auth import easy_login_required
from utils.news_generator import get_latest_news

game = Blueprint('game', __name__)

@game.route('/')
def home():
    """Main homepage of the game"""
    return render_template('index.html')

@game.route('/dashboard')
@easy_login_required
def dashboard():
    # Get current user's nation
    nation = Nation.query.filter_by(user_id=current_user.id).first()
    
    if not nation:
        flash('You do not have a nation. Please contact an administrator.', 'danger')
        return redirect(url_for('auth.logout'))
    
    # Update resources based on time elapsed
    update_resources(nation)
    
    # Get related data
    resources = Resource.query.filter_by(nation_id=nation.id).first()
    military = Military.query.filter_by(nation_id=nation.id).first()
    technologies = Technology.query.filter_by(nation_id=nation.id).all()
    
    # Get top nations for rankings
    top_economic = Nation.query.order_by(Nation.economic_rank).limit(10).all()
    top_military = Nation.query.order_by(Nation.military_rank).limit(10).all()
    top_technology = Nation.query.order_by(Nation.technology_rank).limit(10).all()
    top_overall = Nation.query.order_by(Nation.overall_rank).limit(10).all()
    
    # Update the nation's rankings
    calculate_rankings()
    
    # Add current time for template timer calculations
    now = datetime.utcnow()
    
    # Get latest news for the dashboard widget
    latest_news = get_latest_news(limit=5)
    
    return render_template('dashboard.html', 
                           nation=nation, 
                           resources=resources, 
                           military=military,
                           technologies=technologies,
                           top_economic=top_economic,
                           top_military=top_military,
                           top_technology=top_technology,
                           top_overall=top_overall,
                           latest_news=latest_news,
                           now=now)

@game.route('/population', methods=['GET', 'POST'])
@easy_login_required
def population():
    # Get current user's nation
    nation = Nation.query.filter_by(user_id=current_user.id).first()
    
    # Get resources for display
    resources = Resource.query.filter_by(nation_id=nation.id).first()
    
    if request.method == 'POST':
        try:
            agriculture = float(request.form.get('agriculture', 0))
            industry = float(request.form.get('industry', 0))
            energy = float(request.form.get('energy', 0))
            research = float(request.form.get('research', 0))
            military = float(request.form.get('military', 0))
            
            # Validate total is 100%
            total = agriculture + industry + energy + research + military
            if abs(total - 100) > 0.1:  # Allow a small margin of error for floating point
                flash('Population distribution must total 100%. Current total: {:.1f}%'.format(total), 'danger')
                return redirect(url_for('game.population'))
            
            # Update nation's population distribution
            nation.agriculture_population = agriculture
            nation.industry_population = industry
            nation.energy_population = energy
            nation.research_population = research
            nation.military_population = military
            nation.last_updated = datetime.utcnow()
            
            # Update resource production rates based on new population distribution
            nation.calculate_resource_production()
            
            db.session.commit()
            flash('Population distribution updated successfully.', 'success')
            return redirect(url_for('game.population'))
        except ValueError as e:
            flash('Invalid input: Please enter valid numbers.', 'danger')
            return redirect(url_for('game.population'))
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'danger')
            return redirect(url_for('game.population'))
        
    try:
        # Try with the simplified template first
        return render_template('population_simple.html', nation=nation, resources=resources)
    except Exception as e:
        flash(f'Error loading population page: {str(e)}', 'danger')
        return redirect(url_for('game.dashboard'))

@game.route('/rankings')
@easy_login_required
def rankings():
    try:
        # Get current user's nation
        nation = Nation.query.filter_by(user_id=current_user.id).first()
        
        # Make sure rankings are updated
        calculate_rankings()
        
        # Get all nations for rankings with necessary relationships eager-loaded
        nations = Nation.query.options(
            db.joinedload(Nation.user),
            db.joinedload(Nation.military),
            db.joinedload(Nation.resources),
            db.joinedload(Nation.technologies)
        ).all()
        
        if not nations:
            flash('No nations found in the database.', 'warning')
            nations = []
        
        # Safely categorize nations
        try:
            # For economic rankings use GDP
            economic_rankings = sorted(nations, key=lambda n: n.gdp if n.gdp is not None else 0, reverse=True)
            
            # For military rankings, safely use military power
            def get_military_power(n):
                if n.military:
                    offensive = n.military.offensive_power if n.military.offensive_power is not None else 0
                    defensive = n.military.defensive_power if n.military.defensive_power is not None else 0
                    return offensive + defensive
                return 0
                
            military_rankings = sorted(nations, key=get_military_power, reverse=True)
            
            # For tech rankings, count researched technologies
            tech_rankings = sorted(nations, key=lambda n: len(n.technologies) if n.technologies else 0, reverse=True)
            
            # For overall rankings, use the calculated overall_rank
            overall_rankings = sorted(nations, key=lambda n: n.overall_rank if n.overall_rank is not None else 999)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            flash(f'Error calculating rankings: {str(e)}', 'danger')
            # Provide empty lists to avoid template errors
            economic_rankings = []
            military_rankings = []
            tech_rankings = []
            overall_rankings = []
        
        return render_template('rankings.html', 
                            nation=nation,
                            economic_rankings=economic_rankings,
                            military_rankings=military_rankings,
                            tech_rankings=tech_rankings,
                            overall_rankings=overall_rankings)
    
    except Exception as e:
        # Log the error
        import traceback
        traceback.print_exc()
        # Show error to user
        flash(f'An error occurred loading rankings: {str(e)}', 'danger')
        # Return to dashboard as fallback
        return redirect(url_for('game.dashboard'))

@game.route('/api/resource_history/<resource_type>')
@easy_login_required
def resource_history(resource_type):
    # This would fetch historical data for the specified resource
    # For a real implementation, you would need to store historical data
    # Here we return mock data for demonstration
    
    # In a real implementation, this would query a ResourceHistory table
    # or calculate from periodic snapshots
    
    # Sample data for demonstration - would be replaced with real DB query
    history = [
        {"date": "2023-01-01", "value": 1000},
        {"date": "2023-01-02", "value": 1050},
        {"date": "2023-01-03", "value": 1100},
        {"date": "2023-01-04", "value": 1075},
        {"date": "2023-01-05", "value": 1125}
    ]
    
    return jsonify(history)
