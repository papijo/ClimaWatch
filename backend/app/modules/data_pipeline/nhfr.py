"""
NHFR (National Health Facility Registry) ingestion via HDX dataset download.
Expects a CSV exported from https://data.humdata.org/dataset/nigeria-health-facilities
"""

import csv
import io
from typing import Iterator


def parse_csv(raw_csv: str) -> Iterator[dict]:
    reader = csv.DictReader(io.StringIO(raw_csv))
    for row in reader:
        try:
            yield {
                "name": row.get("facility_name", "").strip(),
                "lga": row.get("lga", "").strip(),
                "state_name": row.get("state", "").strip(),
                "facility_type": _map_type(row.get("facility_type", "")),
                "ownership": _map_ownership(row.get("ownership", "")),
                "latitude": _float_or_none(row.get("latitude")),
                "longitude": _float_or_none(row.get("longitude")),
                "bed_count": _int_or_none(row.get("beds")),
                "source": "nhfr",
            }
        except Exception:
            continue


def _map_type(raw: str) -> str:
    raw = raw.lower()
    if "tertiary" in raw or "teaching" in raw or "federal" in raw:
        return "tertiary"
    if "secondary" in raw or "general" in raw or "specialist" in raw:
        return "secondary"
    return "primary"


def _map_ownership(raw: str) -> str:
    raw = raw.lower()
    if "private" in raw:
        return "private"
    if "ngo" in raw or "mission" in raw or "international" in raw:
        return "ngo"
    if "church" in raw or "mosque" in raw or "faith" in raw:
        return "faith_based"
    return "public"


def _float_or_none(val: str | None) -> float | None:
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


def _int_or_none(val: str | None) -> int | None:
    try:
        return int(val)
    except (TypeError, ValueError):
        return None
