"""
Phase 2 — Data Ingestion

Source (M1-confirmed): Open-Meteo Weather & Flood API
  Weather: https://api.open-meteo.com/v1/forecast
  Flood:   https://flood-api.open-meteo.com/v1/flood
Target:  Noveleta, Cavite (14.4275 N, 120.8808 E)
License: CC BY 4.0 — attribution required.
Fallback: PAGASA ClimDatPh (request-based, not automated).
"""
import json
import logging
import os
from datetime import datetime, timezone

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ---------------------------------------------------------------
# Paths — anchored to this file so the script works from anywhere.
# ingest.py is at cohorts/starter-kit/scripts/ingest.py, so:
#   dirname(__file__)          -> .../starter-kit/scripts
#   join(.., "..", "data/raw") -> .../starter-kit/data/raw
# ---------------------------------------------------------------
RAW_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
RAW_DATA_DIR = os.path.abspath(RAW_DATA_DIR)

# ---------------------------------------------------------------
# Config
# ---------------------------------------------------------------
LAT, LON = 14.4275, 120.8808
TZ = "Asia/Manila"

WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
FLOOD_URL = "https://flood-api.open-meteo.com/v1/flood"

WEATHER_HOURLY = [
    "precipitation",
    "precipitation_probability",
    "temperature_2m",
    "wind_speed_10m",
]
FLOOD_DAILY = [
    "river_discharge",
    "river_discharge_mean",
    "river_discharge_max",
    "river_discharge_min",
]

HEADERS = {
    "Accept": "application/json",
    "User-Agent": "flood-risk-noveleta/0.1 (educational)",
}

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)


def _build_session() -> requests.Session:
    """Session with automatic retries on transient errors (429, 5xx)."""
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=1.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset(["GET"]),
        raise_on_status=False,
    )
    session.mount("https://", HTTPAdapter(max_retries=retry))
    session.headers.update(HEADERS)
    return session


def _fetch(session: requests.Session, url: str, params: dict) -> dict:
    """GET with timeout + error visibility."""
    log.info("GET %s params=%s", url, params)
    try:
        resp = session.get(url, params=params, timeout=30)
    except requests.Timeout:
        log.error("Timeout after 30s: %s", url)
        raise
    except requests.ConnectionError as e:
        log.error("Connection error: %s", e)
        raise

    if resp.status_code != 200:
        log.error("HTTP %s — body: %s", resp.status_code, resp.text[:300])
        resp.raise_for_status()

    log.info("OK %s (%d bytes)", resp.status_code, len(resp.content))
    return resp.json()


def _save_raw(name: str, payload: dict) -> str:
    """Timestamped raw extract. Never overwrites — replayable."""
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = os.path.join(RAW_DATA_DIR, f"{name}_{ts}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    log.info("Saved %s", path)
    return path


def ingest():
    """Pull Open-Meteo weather + flood data and save raw JSON."""
    session = _build_session()

    # --- Weather forecast ---
    weather_params = {
        "latitude": LAT,
        "longitude": LON,
        "hourly": ",".join(WEATHER_HOURLY),
        "forecast_days": 7,
        "timezone": TZ,
    }
    weather = _fetch(session, WEATHER_URL, weather_params)
    _save_raw("weather_forecast", weather)

    # --- Flood forecast ---
    flood_params = {
        "latitude": LAT,
        "longitude": LON,
        "daily": ",".join(FLOOD_DAILY),
        "forecast_days": 30,
        "timezone": TZ,
    }
    flood = _fetch(session, FLOOD_URL, flood_params)
    _save_raw("flood_forecast", flood)


if __name__ == "__main__":
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    ingest()
    print("Ingestion complete. Check data/raw/ for output.")