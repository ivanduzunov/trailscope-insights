
"""Extract hiking relations from an OSM PBF file."""

from pathlib import Path
import subprocess


def extract_hiking_relations(
    input_file: Path,
    output_file: Path,
) -> Path:
    """Extract hiking relations and their referenced objects."""

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    command = [
        "osmium",
        "tags-filter",
        "-o",
        str(output_file),
        str(input_file),
        "r/route=hiking",
        "--overwrite",
    ]

    print("Extracting hiking relations...")

    subprocess.run(
        command,
        check=True,
    )

    print(f"Extraction completed: {output_file}")

    return output_file



"""Extract hiking relations from an OSM PBF file."""

from pathlib import Path
import subprocess

import osmium
import pandas as pd
from pyproj import Geod


GEOD = Geod(ellps="WGS84")


class HikingRouteHandler(osmium.SimpleHandler):
    """Collect hiking routes and calculate their lengths."""

    def __init__(self):
        super().__init__()

        self.way_lengths = {}
        self.routes = []

    def way(self, way):
        """Calculate the geodesic length of a way."""

        coordinates = []

        for node in way.nodes:
            if not node.location.valid():
                self.way_lengths[way.id] = None
                return

            coordinates.append(
                (node.location.lon, node.location.lat)
            )

        if len(coordinates) < 2:
            self.way_lengths[way.id] = None
            return

        length = 0.0

        for start, end in zip(
            coordinates[:-1],
            coordinates[1:],
        ):
            _, _, distance = GEOD.inv(
                start[0],
                start[1],
                end[0],
                end[1],
            )

            length += distance

        self.way_lengths[way.id] = length / 1000

    def relation(self, relation):
        """Collect metadata and member ways."""

        tags = dict(relation.tags)

        if tags.get("route") != "hiking":
            return

        member_way_ids = {
            member.ref
            for member in relation.members
            if member.type == "w"
        }

        mapped_way_ids = [
            way_id
            for way_id in member_way_ids
            if self.way_lengths.get(way_id) is not None
        ]

        total_length = sum(
            self.way_lengths[way_id]
            for way_id in mapped_way_ids
        )

        self.routes.append({
            "osm_relation_id": relation.id,
            "name": tags.get("name"),
            "ref": tags.get("ref"),
            "network": tags.get("network"),
            "operator": tags.get("operator"),
            "website": tags.get("website"),
            "wikidata": tags.get("wikidata"),
            "member_way_count": len(member_way_ids),
            "mapped_way_count": len(mapped_way_ids),
            "missing_way_count": (
                len(member_way_ids) - len(mapped_way_ids)
            ),
            "length_km": total_length,
            "length_complete": (
                len(member_way_ids) == len(mapped_way_ids)
            ),
        })


def process_hiking_routes(
    input_file: Path,
    output_file: Path,
) -> pd.DataFrame:
    """Process extracted OSM hiking routes."""

    handler = HikingRouteHandler()

    print("Processing OSM objects...")

    handler.apply_file(
        str(input_file),
        locations=True,
        idx="flex_mem",
    )

    routes = pd.DataFrame(handler.routes)

    if routes.empty:
        raise ValueError("No hiking relations were found.")

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    routes.to_csv(
        output_file,
        index=False,
    )

    print(f"Processed routes: {len(routes)}")
    print(f"Saved dataset: {output_file}")

    return routes

