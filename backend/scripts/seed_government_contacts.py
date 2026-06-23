"""
Seeds one placeholder government contact (State Ministry of Health) per state.
Idempotent — skips states that already have a contact seeded.
Run from the backend/ directory: python scripts/seed_government_contacts.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.government_contact import GovernmentContact
from app.models.state import State

# (state_code, commissioner_name, email_prefix)
# Format: commissioner@{state_code_lower}.gov.ng
CONTACTS = [
    ("AB", "Commissioner of Health, Abia State"),
    ("AD", "Commissioner of Health, Adamawa State"),
    ("AK", "Commissioner of Health, Akwa Ibom State"),
    ("AN", "Commissioner of Health, Anambra State"),
    ("BA", "Commissioner of Health, Bauchi State"),
    ("BY", "Commissioner of Health, Bayelsa State"),
    ("BE", "Commissioner of Health, Benue State"),
    ("BO", "Commissioner of Health, Borno State"),
    ("CR", "Commissioner of Health, Cross River State"),
    ("DE", "Commissioner of Health, Delta State"),
    ("EB", "Commissioner of Health, Ebonyi State"),
    ("ED", "Commissioner of Health, Edo State"),
    ("EK", "Commissioner of Health, Ekiti State"),
    ("EN", "Commissioner of Health, Enugu State"),
    ("FC", "FCT Minister of State for Health"),
    ("GO", "Commissioner of Health, Gombe State"),
    ("IM", "Commissioner of Health, Imo State"),
    ("JI", "Commissioner of Health, Jigawa State"),
    ("KD", "Commissioner of Health, Kaduna State"),
    ("KN", "Commissioner of Health, Kano State"),
    ("KT", "Commissioner of Health, Katsina State"),
    ("KB", "Commissioner of Health, Kebbi State"),
    ("KO", "Commissioner of Health, Kogi State"),
    ("KW", "Commissioner of Health, Kwara State"),
    ("LA", "Commissioner of Health, Lagos State"),
    ("NA", "Commissioner of Health, Nasarawa State"),
    ("NI", "Commissioner of Health, Niger State"),
    ("OG", "Commissioner of Health, Ogun State"),
    ("ON", "Commissioner of Health, Ondo State"),
    ("OS", "Commissioner of Health, Osun State"),
    ("OY", "Commissioner of Health, Oyo State"),
    ("PL", "Commissioner of Health, Plateau State"),
    ("RI", "Commissioner of Health, Rivers State"),
    ("SO", "Commissioner of Health, Sokoto State"),
    ("TA", "Commissioner of Health, Taraba State"),
    ("YB", "Commissioner of Health, Yobe State"),
    ("ZA", "Commissioner of Health, Zamfara State"),
]


def seed():
    db = SessionLocal()
    try:
        created = 0
        skipped = 0
        for state_code, title in CONTACTS:
            state = db.query(State).filter(State.code == state_code).first()
            if not state:
                print(f"  WARNING: State with code '{state_code}' not found — run seed_states.py first")
                continue

            existing = (
                db.query(GovernmentContact)
                .filter(GovernmentContact.state_id == state.id)
                .first()
            )
            if existing:
                skipped += 1
                continue

            contact = GovernmentContact(
                state_id=state.id,
                name="To Be Updated",
                title=title,
                ministry="State Ministry of Health",
                email=f"health@{state_code.lower()}.gov.ng",
                phone=None,
            )
            db.add(contact)
            created += 1

        db.commit()
        print(f"Government contacts seeded — created: {created}, skipped (already exist): {skipped}")
        if created > 0:
            print("NOTE: Update contact names and emails via the admin panel.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding contacts: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
