"""
Database migration script to create the non_aggression_pacts table
Run this script directly to perform the migration
"""
import sys
import os

# Add the root directory to the path so imports work correctly
sys.path.insert(0, os.path.abspath('.'))

from app import db
from models.diplomatic_relations import non_aggression_pacts

def run_migration():
    """Run the migration to create the non_aggression_pacts table"""
    # Use SQLAlchemy's create_all method to create the table
    db.metadata.create_all(db.engine, [non_aggression_pacts])
    
    print("Migration completed: Created non_aggression_pacts table")
    return True

if __name__ == "__main__":
    run_migration()