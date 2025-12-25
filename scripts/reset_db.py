"""Quick database migration/reset to add thumbnail column"""
import os
import sys

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from models.database import db

app = create_app('development')

with app.app_context():
    # Drop all tables and recreate (safe for dev)
    print("Dropping existing tables...")
    db.drop_all()
    
    print("Creating tables...")
    db.create_all()
    
    print("✓ Database reset complete!")
    print("  - analyses table created")
    print("  - analysis_statistics table created")
    print("  - All columns initialized")
