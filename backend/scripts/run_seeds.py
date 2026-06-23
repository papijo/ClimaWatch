"""
Runs all seed scripts in the correct dependency order.
Run from the backend/ directory: python scripts/run_seeds.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.seed_states import seed as seed_states
from scripts.seed_admin import seed as seed_admin
from scripts.seed_government_contacts import seed as seed_contacts


def main():
    print("=" * 50)
    print("ClimaWatch — Database Seed Runner")
    print("=" * 50)

    print("\n[1/3] Seeding Nigerian states...")
    seed_states()

    print("\n[2/3] Seeding admin accounts...")
    seed_admin()

    print("\n[3/3] Seeding government contacts...")
    seed_contacts()

    print("\n" + "=" * 50)
    print("All seeds complete.")
    print("=" * 50)


if __name__ == "__main__":
    main()
