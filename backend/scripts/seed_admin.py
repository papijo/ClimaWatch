"""
Seeds the Serge admin account directly into the database.
No self-registration flow exists for admin — seed only.
Run from the backend/ directory: python scripts/seed_admin.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.user import User
from app.modules.auth.password import hash_password

ADMIN_ACCOUNTS = [
    {
        "email": "jonathan@climawatch.ng",
        "password": "ClimaWatch@Admin2025!",
        "full_name": "Jonathan Ebhota",
    },
    {
        "email": "ehi@climawatch.ng",
        "password": "ClimaWatch@Admin2025!",
        "full_name": "Ehi Ero-Omoighe",
    },
]


def seed():
    db = SessionLocal()
    try:
        created = 0
        skipped = 0
        for account in ADMIN_ACCOUNTS:
            existing = db.query(User).filter(User.email == account["email"]).first()
            if existing:
                skipped += 1
                print(f"  Skipped (already exists): {account['email']}")
                continue
            user = User(
                email=account["email"],
                password_hash=hash_password(account["password"]),
                full_name=account["full_name"],
                role="admin",
                is_active=True,
            )
            db.add(user)
            created += 1
            print(f"  Created admin: {account['email']}")
        db.commit()
        print(f"\nAdmin accounts — created: {created}, skipped: {skipped}")
        if created > 0:
            print("IMPORTANT: Change the default passwords immediately after first login.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding admin accounts: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
