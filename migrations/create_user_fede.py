"""
Database migration script to create user Fede with Italy as nation
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
    """Run the migration to create user Fede with Italy as nation"""
    print("Starting migration to create user Fede with Italy as nation...")
    
    with app.app_context():
        try:
            # Import models
            from models import User, Nation, Resource, Military, Technology
            
            print("Creating user Fede...")
            # Create user
            fede_user = User(
                username="Fede",
                email="fede@ecoworld.game",
                created_at=datetime.utcnow(),
                last_login=datetime.utcnow()
            )
            fede_user.set_password("Fede1234")  # Set password as requested
            db.session.add(fede_user)
            db.session.flush()  # To get the user ID
            
            # Create Italy nation for Fede
            italy_nation = Nation(
                user_id=fede_user.id,
                name="Italia",
                description="La Repubblica Italiana, un paese nel Sud Europa con una ricca storia e cultura.",
                founded_date=datetime.utcnow(),
                last_updated=datetime.utcnow(),
                total_population=60000000,  # Italy's approximate population
                continent="Europa",
                map_x=52,
                map_y=18,
                svg_id="italy",
                gdp=1800000.0,
                inflation_rate=1.8,
                tax_rate=35.0,
                economic_rank=2,
                military_rank=3,
                technology_rank=2,
                overall_rank=2
            )
            db.session.add(italy_nation)
            db.session.flush()
            
            # Create resources for Italy
            italy_resources = Resource(
                nation_id=italy_nation.id,
                raw_materials=3000.0,
                food=4000.0,  # Italy is known for its cuisine
                energy=2500.0,
                technology_points=600.0,
                currency=45000.0,
                raw_materials_production=300.0,
                food_production=400.0,
                energy_production=250.0,
                technology_production=60.0,
                currency_production=4500.0,
                raw_materials_consumption=200.0,
                food_consumption=200.0,
                energy_consumption=200.0,
                last_updated=datetime.utcnow()
            )
            db.session.add(italy_resources)
            
            # Create military for Italy
            italy_military = Military(
                nation_id=italy_nation.id,
                infantry=4000,
                tanks=150,
                aircraft=40,
                navy=30,  # Strong naval presence due to Mediterranean location
                missiles=8,
                bunkers=15,
                anti_air=12,
                coastal_defenses=15,
                spies=12,
                counter_intelligence=10,
                offensive_power=4000 * 0.1 + 150 * 5 + 40 * 20 + 30 * 30 + 8 * 50,
                defensive_power=15 * 50 + 12 * 30 + 15 * 40,
                espionage_power=12 * 20 - 10 * 5,
                intel_points=120,
                at_war=False,
                last_updated=datetime.utcnow()
            )
            db.session.add(italy_military)
            
            # Commit all changes
            db.session.commit()
            print("Successfully created user Fede with Italy as nation.")
            print("Username: Fede")
            print("Password: Fede1234")
            print("Please log in with these credentials.")
            
        except Exception as e:
            db.session.rollback()
            print(f"Migration failed: {str(e)}")
            raise

if __name__ == "__main__":
    run_migration()