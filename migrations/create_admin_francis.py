"""
Database migration script to delete all existing users and create admin user Francis with Australia as nation
Run this script directly to perform the migration
"""
import sys
import os
from datetime import datetime

# Add the parent directory to the path so we can import the app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import db, app
from sqlalchemy.sql import text as sql_text

def run_migration():
    """Run the migration to create admin user Francis"""
    print("Starting migration to create admin user Francis...")
    
    with app.app_context():
        try:
            # Import models
            from models import User, Nation, Resource, Military, Technology
            
            # Delete all existing users (dangerous! use with caution)
            # User.query.delete()
            # db.session.commit()
            
            print("Creating admin user Francis...")
            # Create admin user
            admin_user = User(
                username="Francis",
                email="admin@ecoworld.game",
                created_at=datetime.utcnow(),
                last_login=datetime.utcnow()
            )
            admin_user.set_password("Admin1234")  # Set password as requested
            db.session.add(admin_user)
            db.session.flush()  # To get the user ID
            
            # Create Australia nation for admin user
            australia_nation = Nation(
                user_id=admin_user.id,
                name="Australia",
                description="The Commonwealth of Australia, a country comprising the mainland of the Australian continent and various islands.",
                founded_date=datetime.utcnow(),
                last_updated=datetime.utcnow(),
                total_population=25000000,  # Australia's approximate population
                continent="Oceania",
                map_x=83,
                map_y=74,
                svg_id="australia",
                gdp=1500000.0,
                inflation_rate=2.2,
                tax_rate=30.0,
                economic_rank=1,
                military_rank=1,
                technology_rank=1,
                overall_rank=1
            )
            db.session.add(australia_nation)
            db.session.flush()
            
            # Create resources for Australia
            australia_resources = Resource(
                nation_id=australia_nation.id,
                raw_materials=5000.0,  # Rich in mining resources
                food=3000.0,
                energy=4000.0,  # Coal and natural gas
                technology_points=1000.0,
                currency=100000.0,
                raw_materials_production=500.0,
                food_production=300.0,
                energy_production=400.0,
                technology_production=100.0,
                currency_production=10000.0,
                raw_materials_consumption=250.0,
                food_consumption=150.0,
                energy_consumption=200.0,
                last_updated=datetime.utcnow()
            )
            db.session.add(australia_resources)
            
            # Create military for Australia
            australia_military = Military(
                nation_id=australia_nation.id,
                infantry=5000,
                tanks=200,
                aircraft=50,
                navy=20,
                missiles=10,
                bunkers=20,
                anti_air=15,
                coastal_defenses=20,
                spies=20,
                counter_intelligence=15,
                offensive_power=5000 * 0.1 + 200 * 5 + 50 * 20 + 20 * 30 + 10 * 50,
                defensive_power=20 * 50 + 15 * 30 + 20 * 40,
                espionage_power=20 * 20 - 15 * 5,
                intel_points=200,
                at_war=False,
                last_updated=datetime.utcnow()
            )
            db.session.add(australia_military)
            
            # Commit all changes
            db.session.commit()
            print("Successfully created admin user Francis with Australia as nation.")
            print("Username: Francis")
            print("Password: Admin1234")
            print("Please log in with these credentials.")
            
        except Exception as e:
            db.session.rollback()
            print(f"Migration failed: {str(e)}")
            raise

if __name__ == "__main__":
    run_migration()