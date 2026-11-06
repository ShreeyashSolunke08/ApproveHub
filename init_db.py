"""
ApproveHub Database Initializer & Migration Utility.
Runs safely on fresh cloud deployments (PostgreSQL or SQLite).
"""
import os
import sys

# Ensure parent directory is in path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from backend.models import db, User, Institution
from backend.fixtures import seed_database

def init_database():
    app = create_app()
    with app.app_context():
        print("Checking database connection and creating tables...")
        db.create_all()
        
        # Seed initial institutional entities if empty
        if not Institution.query.first():
            print("Seeding initial institutional fixtures...")
            seed_database(app)
        else:
            print("Database already contains records. Verifying default assets...")
            admin = User.query.filter_by(role="admin").first()
            if not admin:
                seed_database(app)
                
        print("ApproveHub database initialization complete!")

if __name__ == "__main__":
    init_database()
