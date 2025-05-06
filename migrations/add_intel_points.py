"""
Database migration script to add intel_points field to Military table
Run this script directly to perform the migration
"""
import sys
import os

# Add the parent directory to the path so we can import the app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import db, app
from sqlalchemy.sql import text as sql_text

def run_migration():
    """Run the migration to add intel_points field to Military table"""
    print("Starting migration to add intel_points field to Military table...")
    
    with app.app_context():
        try:
            # Add the intel_points column to Military table
            db.session.execute(sql_text("""
            ALTER TABLE military 
            ADD COLUMN intel_points INTEGER DEFAULT 0
            """))
            
            db.session.commit()
            print("Successfully added intel_points field to Military table.")
            
        except Exception as e:
            db.session.rollback()
            print(f"Migration failed: {str(e)}")
            raise

if __name__ == "__main__":
    run_migration()