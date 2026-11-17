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
        # Ensure all canonical demo profiles exist
        inst = Institution.query.first()
        if inst:
            demo_users = [
                {"name": "Shreeyash Solunke", "email": "shreeyash@vit.edu", "role": "applicant", "department": "Information Technology", "designation": "Student (F.Y. B.Tech)"},
                {"name": "Aditi Kulkarni", "email": "aditi@vit.edu", "role": "applicant", "department": "Information Technology", "designation": "Student (S.Y. B.Tech)"},
                {"name": "Rahul Sharma", "email": "rahul.sharma@vit.edu", "role": "applicant", "department": "Information Technology", "designation": "Student (T.Y. B.Tech)"},
                {"name": "Priya Desai", "email": "priya.desai@vit.edu", "role": "applicant", "department": "Information Technology", "designation": "Student (B.E. Final Year)"},
                {"name": "Prof. Meera Kulkarni", "email": "prof.kulkarni@vit.edu", "role": "approver", "department": "Information Technology", "designation": "Professor"},
                {"name": "Dr. R. Patil", "email": "dr.patil@vit.edu", "role": "approver", "department": "Information Technology", "designation": "HOD"},
                {"name": "Dr. V. Rao", "email": "dr.rao@vit.edu", "role": "approver", "department": "Computer Engineering", "designation": "Dean Academics"},
                {"name": "Institutional Admin", "email": "admin@vit.edu", "role": "admin", "department": "Administration", "designation": "System Controller"},
            ]
            from backend.fixtures import ensure_default_signature
            for u_data in demo_users:
                u = User.query.filter_by(email=u_data["email"]).first()
                if not u:
                    u = User(
                        institution_id=inst.id,
                        name=u_data["name"],
                        email=u_data["email"],
                        role=u_data["role"],
                        department=u_data["department"],
                        designation=u_data["designation"]
                    )
                    u.set_password("demo1234")
                    u.set_pin("1234")
                    db.session.add(u)
                    db.session.commit()
                if u.role in ["approver", "admin"]:
                    ensure_default_signature(u)
        
        print("ApproveHub database initialization complete!")

if __name__ == "__main__":
    init_database()
