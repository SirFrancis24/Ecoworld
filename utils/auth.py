from functools import wraps
from flask import redirect, url_for, flash, session
from flask_login import current_user, login_user
from models import User, Nation, Resource, Military, Technology
from app import db
import traceback

def easy_login_required(f):
    """A custom decorator that either checks if the user is logged in or creates a temporary user"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            # User is already logged in, just proceed as normal
            return f(*args, **kwargs)
        else:
            try:
                # Find or create a demo user
                test_user = User.query.filter_by(username="demo_user").first()
                
                if not test_user:
                    # Create a new demo user
                    test_user = User(
                        username="demo_user",
                        email="demo@example.com"
                    )
                    test_user.set_password("demopassword")
                    db.session.add(test_user)
                    db.session.commit()
                    print("Created new demo user")
                
                # Find or create a nation for this user
                test_nation = Nation.query.filter_by(user_id=test_user.id).first()
                if not test_nation:
                    # Create a test nation
                    test_nation = Nation(
                        user_id=test_user.id,
                        name="Demo Nation",
                        description="A demonstration nation for the game.",
                        # Set initial population distribution
                        agriculture_population=30.0,
                        industry_population=30.0,
                        energy_population=15.0,
                        research_population=10.0,
                        military_population=15.0,
                        # Set other initial values
                        total_population=1000000,
                        gdp=1000000.0,
                        inflation_rate=2.0,
                        tax_rate=20.0
                    )
                    db.session.add(test_nation)
                    db.session.commit()
                    
                    # Create initial resources with default values
                    initial_resources = Resource(
                        nation_id=test_nation.id,
                        raw_materials=1000.0,
                        food=1000.0,
                        energy=1000.0,
                        technology_points=100.0,
                        currency=10000.0,
                        raw_materials_production=100.0,
                        food_production=100.0,
                        energy_production=100.0,
                        technology_production=10.0,
                        currency_production=1000.0,
                        raw_materials_consumption=50.0,
                        food_consumption=50.0,
                        energy_consumption=50.0
                    )
                    db.session.add(initial_resources)
                    
                    # Create initial military
                    initial_military = Military(
                        nation_id=test_nation.id,
                        infantry=1000,
                        tanks=50,
                        aircraft=10,
                        navy=5,
                        missiles=0,
                        bunkers=5,
                        anti_air=5,
                        coastal_defenses=3,
                        spies=2,
                        counter_intelligence=1,
                        offensive_power=500.0,
                        defensive_power=300.0,
                        espionage_power=50.0,
                        intel_points=0,
                        at_war=False
                    )
                    db.session.add(initial_military)
                    
                    db.session.commit()
                    print("Created demo nation with resources and military")
                
                # Log in as this user
                login_user(test_user)
                print(f"Auto-logged in as {test_user.username}")
                
                # Set a session flag for demo mode
                session['demo_mode'] = True
                
                # Now proceed to the original function
                return f(*args, **kwargs)
                
            except Exception as e:
                # Print detailed error information
                traceback.print_exc()
                print(f"Error in auto-login: {str(e)}")
                flash("There was an error with automatic login. Please try again.", "danger")
                return redirect(url_for('auth.login'))
    
    return decorated_function