"""
Database migration script to create espionage-related tables
Run this script directly to perform the migration
"""
import sys
import os
from datetime import datetime, timedelta
import json

# Add the project root directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import Nation, Military, DeployedSpy, SpyMission, SpyReport

def run_migration():
    """Run the migration to create espionage tables"""
    with app.app_context():
        # Check if we need to run this migration
        try:
            # Try to query the DeployedSpy table
            DeployedSpy.query.first()
            print("Espionage tables already exist. Skipping migration.")
            return
        except Exception as e:
            print(f"Preparing to create espionage tables. {str(e)}")
        
        # Create the new tables
        try:
            db.create_all()
            print("Espionage tables created successfully.")
            
            # Update existing Military records to add max_spies
            militaries = Military.query.all()
            for military in militaries:
                if not hasattr(military, 'max_spies') or military.max_spies is None:
                    military.max_spies = 6  # Set a reasonable default
            
            db.session.commit()
            print(f"Updated {len(militaries)} military records with max_spies value.")
            
            # Success message
            print("Migration completed successfully.")
            
        except Exception as e:
            db.session.rollback()
            print(f"Error during migration: {str(e)}")
            raise

if __name__ == "__main__":
    run_migration()