"""
Idempotent seed for all 36 Nigerian states + FCT.
Run from the backend/ directory: python scripts/seed_states.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.state import State

STATES = [
    # (name, code, region, capital, latitude, longitude)
    # --- North Central ---
    ("Benue",    "BE", "North Central", "Makurdi",       7.7312,  8.5368),
    ("FCT Abuja","FC", "North Central", "Abuja",         9.0765,  7.3986),
    ("Kogi",     "KO", "North Central", "Lokoja",        7.8027,  6.7334),
    ("Kwara",    "KW", "North Central", "Ilorin",        8.5373,  4.5444),
    ("Nasarawa", "NA", "North Central", "Lafia",         8.4938,  8.5220),
    ("Niger",    "NI", "North Central", "Minna",         9.6139,  6.5569),
    ("Plateau",  "PL", "North Central", "Jos",           9.8965,  8.8583),
    # --- North East ---
    ("Adamawa",  "AD", "North East",    "Yola",          9.2035, 12.4954),
    ("Bauchi",   "BA", "North East",    "Bauchi",       10.3158,  9.8442),
    ("Borno",    "BO", "North East",    "Maiduguri",    11.8333, 13.1500),
    ("Gombe",    "GO", "North East",    "Gombe",        10.2791, 11.1671),
    ("Taraba",   "TA", "North East",    "Jalingo",       8.9010, 11.3630),
    ("Yobe",     "YB", "North East",    "Damaturu",     11.7480, 11.9660),
    # --- North West ---
    ("Jigawa",   "JI", "North West",    "Dutse",        11.8631,  9.3564),
    ("Kaduna",   "KD", "North West",    "Kaduna",       10.5105,  7.4165),
    ("Kano",     "KN", "North West",    "Kano",         12.0022,  8.5919),
    ("Katsina",  "KT", "North West",    "Katsina",      12.9889,  7.6006),
    ("Kebbi",    "KB", "North West",    "Birnin Kebbi", 12.4539,  4.1975),
    ("Sokoto",   "SO", "North West",    "Sokoto",       13.0059,  5.2476),
    ("Zamfara",  "ZA", "North West",    "Gusau",        12.1704,  6.6624),
    # --- South East ---
    ("Abia",     "AB", "South East",    "Umuahia",       5.5320,  7.4860),
    ("Anambra",  "AN", "South East",    "Awka",          6.2088,  7.0664),
    ("Ebonyi",   "EB", "South East",    "Abakaliki",     6.3249,  8.1137),
    ("Enugu",    "EN", "South East",    "Enugu",         6.4584,  7.5464),
    ("Imo",      "IM", "South East",    "Owerri",        5.4831,  7.0333),
    # --- South South ---
    ("Akwa Ibom","AK", "South South",   "Uyo",           5.0510,  7.9339),
    ("Bayelsa",  "BY", "South South",   "Yenagoa",       4.9408,  6.2649),
    ("Cross River","CR","South South",  "Calabar",       4.9757,  8.3417),
    ("Delta",    "DE", "South South",   "Asaba",         6.2059,  6.6848),
    ("Edo",      "ED", "South South",   "Benin City",    6.3350,  5.6037),
    ("Rivers",   "RI", "South South",   "Port Harcourt", 4.8156,  7.0498),
    # --- South West ---
    ("Ekiti",    "EK", "South West",    "Ado Ekiti",     7.6218,  5.2207),
    ("Lagos",    "LA", "South West",    "Ikeja",         6.5227,  3.6218),
    ("Ogun",     "OG", "South West",    "Abeokuta",      7.1557,  3.3451),
    ("Ondo",     "ON", "South West",    "Akure",         7.2526,  5.1937),
    ("Osun",     "OS", "South West",    "Osogbo",        7.7719,  4.5624),
    ("Oyo",      "OY", "South West",    "Ibadan",        7.3775,  3.9470),
]


def seed():
    db = SessionLocal()
    try:
        created = 0
        skipped = 0
        for name, code, region, capital, lat, lng in STATES:
            existing = db.query(State).filter(State.code == code).first()
            if existing:
                skipped += 1
                continue
            state = State(
                name=name,
                code=code,
                region=region,
                capital=capital,
                latitude=lat,
                longitude=lng,
                current_risk_level="LOW",
            )
            db.add(state)
            created += 1
        db.commit()
        print(f"States seeded — created: {created}, skipped (already exist): {skipped}")
    except Exception as e:
        db.rollback()
        print(f"Error seeding states: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
