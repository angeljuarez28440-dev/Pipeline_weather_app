"""Pull current weather from the Open-Meteo API and save the raw JSON to disk."""

import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

API_URL = "https://api.open-meteo.com/v1/forecast"
RAW_DIR = Path("data/raw")
MAX_RETRIES = 3
TIMEOUT_SECONDS = 10

# Add or change cities here. Each one becomes its own raw file per run.
CITIES = {
    "atlanta": (33.749, -84.388),
    "new_york": (40.7128, -74.006),
    "london": (51.5072, -0.1276),
    "tokyo": (35.6895, 139.6917)
    
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)


def fetch_weather(latitude: float, longitude: float) -> dict:
    """Call the API for one location. Retries on failure with a growing delay."""
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation,pressure_msl",
    }

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(API_URL, params=params, timeout=TIMEOUT_SECONDS)
            response.raise_for_status()  # raises on 4xx/5xx responses
            return response.json()
        except requests.RequestException as exc:
            logger.warning("Attempt %d/%d failed: %s", attempt, MAX_RETRIES, exc)
            if attempt == MAX_RETRIES:
                logger.error("Giving up after %d attempts", MAX_RETRIES)
                raise
            time.sleep(2**attempt)  # wait 2s, then 4s


def save_raw(data: dict, city: str, raw_dir: Path = RAW_DIR) -> Path:
    """Write the untouched API response to a timestamped JSON file."""
    raw_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = raw_dir / f"{city}_{timestamp}.json"
    path.write_text(json.dumps(data, indent=2))
    return path


def run() -> None:
    """Fetch and store weather for every city. One failure won't stop the rest."""
    logger.info("Ingestion run started for %d cities", len(CITIES))
    succeeded = 0

    for city, (lat, lon) in CITIES.items():
        try:
            data = fetch_weather(lat, lon)
            path = save_raw(data, city)
            logger.info("Saved %s -> %s", city, path)
            succeeded += 1
        except Exception:
            logger.exception("Failed to ingest %s", city)

    logger.info("Run finished: %d/%d cities succeeded", succeeded, len(CITIES))


if __name__ == "__main__":
    run()