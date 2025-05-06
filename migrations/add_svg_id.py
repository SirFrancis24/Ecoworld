"""
Database migration script to add svg_id field to Nation table
Run this script directly to perform the migration
"""
import sys
import os
from datetime import datetime

# Add the parent directory to the path so we can import the app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import db, app

def run_migration():
    """Run the migration to add svg_id field to Nation table"""
    print("Starting migration to add svg_id field to Nation table...")
    
    with app.app_context():
        try:
            # Check if column exists first
            from sqlalchemy import text
            sql = text("SELECT column_name FROM information_schema.columns WHERE table_name='nation' AND column_name='svg_id'")
            result = db.session.execute(sql).fetchall()
            
            if result:
                print("Column svg_id already exists in Nation table. Migration not needed.")
                return
                
            print("Adding svg_id column to Nation table...")
            # Add the svg_id column to the Nation table
            sql = text("ALTER TABLE nation ADD COLUMN svg_id VARCHAR(50)")
            db.session.execute(sql)
            db.session.commit()
            
            print("Setting svg_id values for existing nations...")
            # Update existing nations with appropriate svg_id values
            sql_updates = [
                # Nord America
                "UPDATE nation SET svg_id = 'usa' WHERE name LIKE '%United States%'",
                "UPDATE nation SET svg_id = 'canada' WHERE name LIKE '%Canada%'",
                "UPDATE nation SET svg_id = 'mexico' WHERE name LIKE '%Mexico%' OR name LIKE '%Messico%'",
                "UPDATE nation SET svg_id = 'greenland' WHERE name LIKE '%Greenland%' OR name LIKE '%Groenlandia%'",
                "UPDATE nation SET svg_id = 'alaska' WHERE name LIKE '%Alaska%'",
                
                # Sud America
                "UPDATE nation SET svg_id = 'brazil' WHERE name LIKE '%Brazil%' OR name LIKE '%Brasile%'",
                "UPDATE nation SET svg_id = 'argentina' WHERE name LIKE '%Argentina%'",
                "UPDATE nation SET svg_id = 'colombia' WHERE name LIKE '%Colombia%'",
                "UPDATE nation SET svg_id = 'chile' WHERE name LIKE '%Chile%' OR name LIKE '%Cile%'",
                
                # Europa Occidentale
                "UPDATE nation SET svg_id = 'uk' WHERE name LIKE '%United Kingdom%' OR name LIKE '%Regno Unito%'",
                "UPDATE nation SET svg_id = 'france' WHERE name LIKE '%France%' OR name LIKE '%Francia%'",
                "UPDATE nation SET svg_id = 'germany' WHERE name LIKE '%Germany%' OR name LIKE '%Germania%'",
                "UPDATE nation SET svg_id = 'italy' WHERE name LIKE '%Italy%' OR name LIKE '%Italia%'",
                "UPDATE nation SET svg_id = 'spain' WHERE name LIKE '%Spain%' OR name LIKE '%Spagna%'",
                
                # Europa Orientale
                "UPDATE nation SET svg_id = 'poland' WHERE name LIKE '%Poland%' OR name LIKE '%Polonia%'",
                "UPDATE nation SET svg_id = 'ukraine' WHERE name LIKE '%Ukraine%' OR name LIKE '%Ucraina%'",
                "UPDATE nation SET svg_id = 'russia' WHERE name LIKE '%Russia%'",
                
                # Africa
                "UPDATE nation SET svg_id = 'egypt' WHERE name LIKE '%Egypt%' OR name LIKE '%Egitto%'",
                "UPDATE nation SET svg_id = 'nigeria' WHERE name LIKE '%Nigeria%'",
                "UPDATE nation SET svg_id = 'south-africa' WHERE name LIKE '%South Africa%' OR name LIKE '%Sudafrica%'",
                
                # Medio Oriente
                "UPDATE nation SET svg_id = 'saudi-arabia' WHERE name LIKE '%Saudi Arabia%' OR name LIKE '%Arabia Saudita%'",
                "UPDATE nation SET svg_id = 'iran' WHERE name LIKE '%Iran%'",
                
                # Asia
                "UPDATE nation SET svg_id = 'china' WHERE name LIKE '%China%' OR name LIKE '%Cina%'",
                "UPDATE nation SET svg_id = 'india' WHERE name LIKE '%India%'",
                "UPDATE nation SET svg_id = 'japan' WHERE name LIKE '%Japan%' OR name LIKE '%Giappone%'",
                "UPDATE nation SET svg_id = 'south-korea' WHERE name LIKE '%South Korea%' OR name LIKE '%Corea del Sud%'",
                
                # Oceania
                "UPDATE nation SET svg_id = 'australia' WHERE name LIKE '%Australia%'",
                "UPDATE nation SET svg_id = 'new-zealand' WHERE name LIKE '%New Zealand%' OR name LIKE '%Nuova Zelanda%'",
                
                # Regione Extra
                "UPDATE nation SET svg_id = 'antarctica' WHERE name LIKE '%Antarctica%' OR name LIKE '%Antartide%'"
            ]
            
            for sql_update in sql_updates:
                db.session.execute(text(sql_update))
                
            db.session.commit()
            print("Migration completed successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"Migration failed: {str(e)}")
            raise

if __name__ == "__main__":
    run_migration()