"""
CLI to trigger batch vulnerability scoring for all states.
Run from the backend/ directory: python scripts/run_scoring.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.modules.vulnerability_scoring.runner import score_all


def main():
    print("ClimaWatch — Vulnerability Scoring")
    print("=" * 40)
    db = SessionLocal()
    try:
        results = score_all(db)
        total_lgas = sum(r["lgas"] for r in results.values())
        total_facilities = sum(r["facilities"] for r in results.values())
        for state_name, counts in results.items():
            if counts["lgas"] > 0 or counts["facilities"] > 0:
                print(f"  {state_name}: {counts['lgas']} LGAs, {counts['facilities']} facilities")
        print(f"\nTotal: {total_lgas} LGA scores, {total_facilities} facility scores")
    except Exception as e:
        print(f"Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
