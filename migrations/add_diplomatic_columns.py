"""
Database migration script to add diplomatic fields to the Nation model
Run this script directly to perform the migration
"""

import sys
import os
from datetime import datetime
from sqlalchemy import create_engine, MetaData, Table, Column, String, Float
from sqlalchemy.ext.declarative import declarative_base

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import get_config

def run_migration():
    """Run the migration to add diplomatic fields to Nation table"""
    config = get_config()
    engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
    
    # Connect to the engine
    connection = engine.connect()
    
    try:
        # Get the metadata and reflect the table
        metadata = MetaData()
        metadata.reflect(bind=engine)
        
        # Get the Nation table
        nation_table = Table('nation', metadata, autoload=True, autoload_with=engine)
        
        # Check if the columns already exist
        existing_columns = [column.name for column in nation_table.columns]
        
        # Add continent column if it doesn't exist
        if 'continent' not in existing_columns:
            print("Adding 'continent' column...")
            connection.execute('ALTER TABLE nation ADD COLUMN continent VARCHAR(50) DEFAULT \'Europe\'')
        
        # Add map_x column if it doesn't exist
        if 'map_x' not in existing_columns:
            print("Adding 'map_x' column...")
            connection.execute('ALTER TABLE nation ADD COLUMN map_x FLOAT DEFAULT 50.0')
        
        # Add map_y column if it doesn't exist
        if 'map_y' not in existing_columns:
            print("Adding 'map_y' column...")
            connection.execute('ALTER TABLE nation ADD COLUMN map_y FLOAT DEFAULT 30.0')
            
        # Set initial values for existing nations
        print("Setting initial values for existing nations...")
        
        # Set positions for existing nations based on their IDs to spread them across the map
        connection.execute("""
            UPDATE nation 
            SET map_x = (id * 10) % 90 + 5,
                map_y = (id * 15) % 80 + 10,
                continent = CASE 
                    WHEN id % 6 = 0 THEN 'North America'
                    WHEN id % 6 = 1 THEN 'South America'
                    WHEN id % 6 = 2 THEN 'Europe'
                    WHEN id % 6 = 3 THEN 'Africa'
                    WHEN id % 6 = 4 THEN 'Asia'
                    ELSE 'Australia'
                END
        """)
        
        print("Migration completed successfully!")
    except Exception as e:
        print(f"Error during migration: {e}")
    finally:
        connection.close()

if __name__ == "__main__":
    run_migration()