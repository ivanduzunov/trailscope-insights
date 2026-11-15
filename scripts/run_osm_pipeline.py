
"""Run the Bulgaria hiking data extraction pipeline."""

import sys
from pathlib import Path

# Add project root to Python import path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.data_collection.osm_extractor import (
    extract_hiking_relations,
    process_hiking_routes,
)


RAW_DIR = Path("data/raw/osm")
INTERIM_DIR = Path("data/interim/osm")
PROCESSED_DIR = Path("data/processed")

COUNTRY = "bulgaria"
SNAPSHOT = "250101"


def main():
    """Execute the complete OSM extraction workflow."""

    source_file = (
        RAW_DIR / f"{COUNTRY}-{SNAPSHOT}.osm.pbf"
    )

    filtered_file = (
        INTERIM_DIR / f"{COUNTRY}-hiking.osm.pbf"
    )

    output_file = (
        PROCESSED_DIR / f"{COUNTRY}-hiking-routes.csv"
    )

    if not source_file.exists():
        raise FileNotFoundError(
            f"OSM source file not found: {source_file}"
        )

    extract_hiking_relations(
        input_file=source_file,
        output_file=filtered_file,
    )

    routes = process_hiking_routes(
        input_file=filtered_file,
        output_file=output_file,
    )

    print("\n========== PIPELINE SUMMARY ==========")
    print(f"Country: {COUNTRY}")
    print(f"Snapshot: {SNAPSHOT}")
    print(f"Total routes: {len(routes)}")
    print(
        f"Total mapped route length: "
        f"{routes['length_km'].sum():.2f} km"
    )
    print(
        f"Complete routes: "
        f"{routes['length_complete'].sum()}"
    )
    print("======================================")


if __name__ == "__main__":
    main()
