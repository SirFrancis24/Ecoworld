"""
Database migration script to create 5 bot nations with random names
Run this script directly to perform the migration
"""
import sys
import os
import random
from datetime import datetime

# Add the parent directory to the path so we can import the app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import db, app
from models import User, Nation, Resource, Military, Technology

# Lista di nomi per i bot
FIRST_NAMES = ["Alexander", "Victor", "Sophia", "Isabella", "William", "James", "Emma", "Olivia", "Leonardo", "Marcus"]
LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis", "Garcia", "Rodriguez", "Wilson"]

# Lista di paesi disponibili per i bot
COUNTRIES = [
    {"name": "Canada", "continent": "North America", "map_x": 15, "map_y": 8, "svg_id": "canada"},
    {"name": "Brazil", "continent": "South America", "map_x": 22, "map_y": 33, "svg_id": "brazil"},
    {"name": "Germany", "continent": "Europe", "map_x": 48, "map_y": 13, "svg_id": "germany"},
    {"name": "Russia", "continent": "Europe/Asia", "map_x": 58, "map_y": 12, "svg_id": "russia"},
    {"name": "China", "continent": "Asia", "map_x": 69, "map_y": 19, "svg_id": "china"},
    {"name": "India", "continent": "Asia", "map_x": 63, "map_y": 24, "svg_id": "india"},
    {"name": "South Africa", "continent": "Africa", "map_x": 48, "map_y": 33, "svg_id": "south_africa"},
    {"name": "Japan", "continent": "Asia", "map_x": 76, "map_y": 18, "svg_id": "japan"}
]

def create_bot_nation(bot_index):
    """Create a bot user and nation with random attributes"""
    # Generate random name
    first_name = random.choice(FIRST_NAMES)
    last_name = random.choice(LAST_NAMES)
    username = f"{first_name}{last_name}"
    email = f"{username.lower()}@ecoworld.bot"
    
    # Create bot user
    bot_user = User(
        username=username,
        email=email,
        created_at=datetime.utcnow(),
        last_login=datetime.utcnow()
    )
    bot_user.set_password(f"Bot{bot_index}Pass")
    db.session.add(bot_user)
    db.session.flush()
    
    # Select random country
    country = random.choice(COUNTRIES)
    COUNTRIES.remove(country)  # Remove to avoid duplicates
    
    # Random population between 5 and 50 million
    population = random.randint(5, 50) * 1000000
    
    # Create bot nation
    bot_nation = Nation(
        user_id=bot_user.id,
        name=country["name"],
        description=f"A nation governed by {first_name} {last_name}.",
        founded_date=datetime.utcnow(),
        last_updated=datetime.utcnow(),
        total_population=population,
        continent=country["continent"],
        map_x=country["map_x"],
        map_y=country["map_y"],
        svg_id=country["svg_id"],
        gdp=population / 10,
        inflation_rate=random.uniform(1.0, 5.0),
        tax_rate=random.uniform(15.0, 40.0),
        economic_rank=bot_index+3,
        military_rank=bot_index+3,
        technology_rank=bot_index+3,
        overall_rank=bot_index+3
    )
    db.session.add(bot_nation)
    db.session.flush()
    
    # Base resources with random variations
    base_resources = 1000 + random.randint(0, 4000)
    bot_resources = Resource(
        nation_id=bot_nation.id,
        raw_materials=base_resources + random.randint(-500, 1500),
        food=base_resources + random.randint(-500, 1500),
        energy=base_resources + random.randint(-500, 1500),
        technology_points=base_resources / 10 + random.randint(-50, 150),
        currency=base_resources * 10 + random.randint(-5000, 15000),
        raw_materials_production=100 + random.randint(0, 400),
        food_production=100 + random.randint(0, 400),
        energy_production=100 + random.randint(0, 400),
        technology_production=10 + random.randint(0, 40),
        currency_production=1000 + random.randint(0, 4000),
        raw_materials_consumption=50 + random.randint(0, 200),
        food_consumption=50 + random.randint(0, 200),
        energy_consumption=50 + random.randint(0, 200),
        last_updated=datetime.utcnow()
    )
    db.session.add(bot_resources)
    
    # Military with random strength
    infantry_base = 1000 + random.randint(0, 9000)
    bot_military = Military(
        nation_id=bot_nation.id,
        infantry=infantry_base,
        tanks=infantry_base // 20,
        aircraft=infantry_base // 100,
        navy=infantry_base // 200,
        missiles=infantry_base // 500,
        bunkers=infantry_base // 200,
        anti_air=infantry_base // 250,
        coastal_defenses=infantry_base // 300,
        spies=infantry_base // 400,
        counter_intelligence=infantry_base // 500,
        offensive_power=infantry_base * 0.1 + (infantry_base // 20) * 5 + (infantry_base // 100) * 20 + (infantry_base // 200) * 30 + (infantry_base // 500) * 50,
        defensive_power=(infantry_base // 200) * 50 + (infantry_base // 250) * 30 + (infantry_base // 300) * 40,
        espionage_power=(infantry_base // 400) * 20 - (infantry_base // 500) * 5,
        intel_points=random.randint(50, 300),
        at_war=False,
        last_updated=datetime.utcnow()
    )
    db.session.add(bot_military)
    
    print(f"Created bot nation: {country['name']} ruled by {first_name} {last_name}")
    return bot_user, bot_nation

def run_migration():
    """Run the migration to create 5 bot nations"""
    print("Starting migration to create 5 bot nations...")
    
    with app.app_context():
        try:
            # Create 5 bot nations
            for i in range(5):
                create_bot_nation(i)
            
            # Commit all changes
            db.session.commit()
            print("Successfully created 5 bot nations.")
        except Exception as e:
            db.session.rollback()
            print(f"Migration failed: {str(e)}")
            raise

if __name__ == "__main__":
    run_migration()