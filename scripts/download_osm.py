
"""Download a historical OpenStreetMap extract."""

from pathlib import Path

import requests


BASE_URL = "https://download.geofabrik.de/europe"

COUNTRY = "bulgaria"
SNAPSHOT = "250101"

OUTPUT_DIR = Path("data/raw/osm")


def download_osm_extract(
    country: str,
    snapshot: str,
    output_dir: Path,
) -> Path:
    """Download a historical Geofabrik PBF extract."""

    output_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{country}-{snapshot}.osm.pbf"
    file_path = output_dir / filename

    url = f"{BASE_URL}/{filename}"

    if file_path.exists():
        print(f"File already exists: {file_path}")
        return file_path

    print(f"Downloading: {url}")

    response = requests.get(
        url,
        stream=True,
        timeout=(30, 120),
    )
    response.raise_for_status()

    total_size = int(response.headers.get("content-length", 0))
    downloaded = 0

    try:
        with file_path.open("wb") as file:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if not chunk:
                    continue

                file.write(chunk)
                downloaded += len(chunk)

                if total_size:
                    progress = downloaded / total_size * 100
                    print(
                        f"\rProgress: {progress:.1f}%",
                        end="",
                    )

        print("\nDownload completed.")

    except Exception:
        file_path.unlink(missing_ok=True)
        raise

    return file_path


if __name__ == "__main__":
    downloaded_file = download_osm_extract(
        country=COUNTRY,
        snapshot=SNAPSHOT,
        output_dir=OUTPUT_DIR,
    )

    print(f"Saved to: {downloaded_file}")
