"""
Database migration script to add predefined nations to the database
Run this script directly to perform the migration
"""
import sys
import os
from datetime import datetime

# Add the parent directory to the path so we can import the app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from app import db, app

def run_migration():
    """Run the migration to add predefined nations to the database"""
    print("Starting migration to add predefined nations...")
    
    with app.app_context():
        # Check if we already have nations in the database
        from models import Nation, User, Resource, Military, Technology
        
        # Force migration regardless of existing nations (comment this out to restore the check)
        existing_nations = []
        # existing_nations = Nation.query.all()
        # if existing_nations:
        #     print(f"Found {len(existing_nations)} existing nations. Migration not needed.")
        #     return
            
        print("Creating predefined nations...")
        
        # Define the nations with map coordinates exactly matching the SVG map
        predefined_nations = [
            # Nord America
            {"name": "United States", "continent": "Nord America", "map_x": 160, "map_y": 170, "svg_id": "usa"},
            {"name": "Canada", "continent": "Nord America", "map_x": 150, "map_y": 110, "svg_id": "canada"},
            {"name": "Mexico", "continent": "Nord America", "map_x": 130, "map_y": 200, "svg_id": "mexico"},
            {"name": "Groenlandia", "continent": "Nord America", "map_x": 280, "map_y": 80, "svg_id": "greenland"},
            {"name": "Alaska", "continent": "Nord America", "map_x": 60, "map_y": 90, "svg_id": "alaska"},
            
            # Sud America
            {"name": "Brasile", "continent": "Sud America", "map_x": 220, "map_y": 330, "svg_id": "brazil"},
            {"name": "Argentina", "continent": "Sud America", "map_x": 190, "map_y": 390, "svg_id": "argentina"},
            {"name": "Colombia", "continent": "Sud America", "map_x": 180, "map_y": 260, "svg_id": "colombia"},
            {"name": "Cile", "continent": "Sud America", "map_x": 150, "map_y": 410, "svg_id": "chile"},
            
            # Europa Occidentale
            {"name": "Regno Unito", "continent": "Europa Occidentale", "map_x": 405, "map_y": 140, "svg_id": "uk"},
            {"name": "Francia", "continent": "Europa Occidentale", "map_x": 410, "map_y": 180, "svg_id": "france"},
            {"name": "Germania", "continent": "Europa Occidentale", "map_x": 440, "map_y": 150, "svg_id": "germany"},
            {"name": "Italia", "continent": "Europa Occidentale", "map_x": 440, "map_y": 215, "svg_id": "italy"},
            {"name": "Spagna", "continent": "Europa Occidentale", "map_x": 380, "map_y": 210, "svg_id": "spain"},
            
            # Europa Orientale
            {"name": "Russia", "continent": "Europa Orientale", "map_x": 580, "map_y": 110, "svg_id": "russia"},
            {"name": "Ucraina", "continent": "Europa Orientale", "map_x": 510, "map_y": 190, "svg_id": "ukraine"},
            {"name": "Polonia", "continent": "Europa Orientale", "map_x": 470, "map_y": 160, "svg_id": "poland"},
            
            # Africa
            {"name": "Egitto", "continent": "Africa", "map_x": 460, "map_y": 250, "svg_id": "egypt"},
            {"name": "Nigeria", "continent": "Africa", "map_x": 415, "map_y": 300, "svg_id": "nigeria"},
            {"name": "Sudafrica", "continent": "Africa", "map_x": 450, "map_y": 380, "svg_id": "south-africa"},
            
            # Medio Oriente
            {"name": "Arabia Saudita", "continent": "Medio Oriente", "map_x": 510, "map_y": 265, "svg_id": "saudi-arabia"},
            {"name": "Iran", "continent": "Medio Oriente", "map_x": 545, "map_y": 230, "svg_id": "iran"},
            
            # Asia
            {"name": "Cina", "continent": "Asia", "map_x": 670, "map_y": 150, "svg_id": "china"},
            {"name": "India", "continent": "Asia", "map_x": 620, "map_y": 210, "svg_id": "india"},
            {"name": "Giappone", "continent": "Asia", "map_x": 760, "map_y": 150, "svg_id": "japan"},
            {"name": "Corea del Sud", "continent": "Asia", "map_x": 735, "map_y": 185, "svg_id": "south-korea"},
            
            # Oceania
            {"name": "Australia", "continent": "Oceania", "map_x": 810, "map_y": 350, "svg_id": "australia"},
            {"name": "Nuova Zelanda", "continent": "Oceania", "map_x": 885, "map_y": 375, "svg_id": "new-zealand"},
            
            # Regione Extra
            {"name": "Antartide", "continent": "Regione Extra", "map_x": 600, "map_y": 585, "svg_id": "antarctica"},
        ]
        
        # Add bot users and their nations
        for i, nation_data in enumerate(predefined_nations):
            # Create bot user
            bot_user = User(
                username=f"ai_{nation_data['name'].lower().replace(' ', '_')}",
                email=f"ai_{nation_data['name'].lower().replace(' ', '_')}@ecoworld.game",
                created_at=datetime.utcnow(),
                last_login=datetime.utcnow()
            )
            bot_user.set_password("ai_controlled_nation")
            db.session.add(bot_user)
            db.session.flush()  # To get the user ID
            
            # Create nation for bot
            nation = Nation(
                user_id=bot_user.id,
                name=nation_data['name'],
                description=f"AI-controlled nation of {nation_data['name']}",
                founded_date=datetime.utcnow(),
                last_updated=datetime.utcnow(),
                total_population=1000000 + (i * 50000),  # Varying population
                continent=nation_data['continent'],
                map_x=nation_data['map_x'],
                map_y=nation_data['map_y'],
                svg_id=nation_data['svg_id'],  # Add the SVG ID
                gdp=1000000.0 + (i * 100000),
                inflation_rate=2.0 + (i % 5),
                tax_rate=20.0 + (i % 10),
                economic_rank=i+1,
                military_rank=len(predefined_nations) - i,
                technology_rank=((i * 3) % len(predefined_nations)) + 1,
                overall_rank=((i * 2) % len(predefined_nations)) + 1
            )
            db.session.add(nation)
            db.session.flush()
            
            # Create resources for nation
            resource = Resource(
                nation_id=nation.id,
                raw_materials=1000.0 + (i * 100),
                food=1000.0 + (i * 80),
                energy=1000.0 + (i * 120),
                technology_points=100.0 + (i * 10),
                currency=10000.0 + (i * 1000),
                raw_materials_production=100.0 + (i % 50),
                food_production=100.0 + (i % 40),
                energy_production=100.0 + (i % 60),
                technology_production=10.0 + (i % 5),
                currency_production=1000.0 + (i % 500),
                raw_materials_consumption=50.0 + (i % 25),
                food_consumption=50.0 + (i % 20),
                energy_consumption=50.0 + (i % 30),
                last_updated=datetime.utcnow()
            )
            db.session.add(resource)
            
            # Create military for nation
            military = Military(
                nation_id=nation.id,
                infantry=1000 + (i * 100),
                tanks=50 + (i * 5),
                aircraft=10 + (i * 1),
                navy=5 + (i % 5),
                missiles=i % 10,
                bunkers=5 + (i % 5),
                anti_air=5 + (i % 5),
                coastal_defenses=3 + (i % 3),
                spies=2 + (i % 3),
                counter_intelligence=1 + (i % 2),
                offensive_power=(1000 + (i * 100)) * 0.1 + (50 + (i * 5)) * 5 + (10 + (i * 1)) * 20 + (5 + (i % 5)) * 30 + (i % 10) * 50,
                defensive_power=(5 + (i % 5)) * 50 + (5 + (i % 5)) * 30 + (3 + (i % 3)) * 40,
                espionage_power=(2 + (i % 3)) * 20 - (1 + (i % 2)) * 5,
                at_war=False,
                last_updated=datetime.utcnow()
            )
            db.session.add(military)
        
        # Commit all changes
        db.session.commit()
        print(f"Successfully added {len(predefined_nations)} predefined nations to the database.")

if __name__ == "__main__":
    run_migration()