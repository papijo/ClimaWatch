"""
CLI script to ingest NHFR health facility data from a CSV file.
Run from the backend/ directory:
  python scripts/ingest_nhfr.py path/to/nhfr_export.csv
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.modules.data_pipeline.nhfr import ingest


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/ingest_nhfr.py <path_to_csv>")
        sys.exit(1)

    csv_path = sys.argv[1]
    if not os.path.isfile(csv_path):
        print(f"File not found: {csv_path}")
        sys.exit(1)

    with open(csv_path, encoding="utf-8") as f:
        raw_csv = f.read()

    print(f"Ingesting facilities from {csv_path}...")
    db = SessionLocal()
    try:
        result = ingest(raw_csv, db)
        print(f"Done — created: {result['created']}, skipped: {result['skipped']}, unresolved: {result['unresolved_state']}")
    except Exception as e:
        print(f"Error during ingest: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
