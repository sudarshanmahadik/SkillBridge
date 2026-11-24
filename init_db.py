import sys, os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from app.extensions import db
from seed_data import seed_database

if __name__ == '__main__':
    print("==================================================")
    print("SkillBridge Database Initialization & Seeding")
    print("==================================================")
    seed_database()
    print("Database tables created and sample data seeded successfully!")
