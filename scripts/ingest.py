"""
Week 5 — Robust API ingestion for Noveleta flood-risk monitoring.
Sources:
  - Open-Meteo Weather API  (https://api.open-meteo.com/v1/forecast)
  - Open-Meteo Flood API    (https://flood-api.open-meteo.com/v1/flood)
License: CC BY 4.0 — attribution required in any public dashboard.
"""
from __future__ import annotations

import json
import logging
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ---------- Config ----------
LAT, LON = 14.4275, 120.8808
TZ = "Asia/Manila"
RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
FLOOD_URL = "https://flood-api.open-meteo.com/v1/flood"

WEATHER_HOURLY = [
    "precipitation",
    "rain",
    "probability_of_precipitation",
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
    "User-Agent": "flood-risk-noveleta/0.1 (educational; contact: you@example.com)",
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger(__name__)


# ---------- HTTP session with retries ----------
def build_session() -> requests.Session:
    """Session with automatic retries on transient errors (429, 5xx)."""
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=1.5,               # 1.5s, 3s, 6s between retries
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset(["GET"]),
        raise_on_status=False,
    )
    session.mount("https://", HTTPAdapter(max_retries=retry))
    session.headers.update(HEADERS)
    return session


# ---------- Core fetch ----------
def fetch(session: requests.Session, url: str, params: dict) -> dict:
    """GET with timeout + explicit error visibility."""
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


# ---------- Source-specific wrappers ----------
def pull_weather(session, forecast_days: int = 7) -> dict:
    params = {
        "latitude": LAT,
        "longitude": LON,
        "hourly": ",".join(WEATHER_HOURLY),
        "forecast_days": forecast_days,
        "timezone": TZ,
    }
    return fetch(session, WEATHER_URL, params)


def pull_flood_forecast(session, forecast_days: int = 30) -> dict:
    params = {
        "latitude": LAT,
        "longitude": LON,
        "daily": ",".join(FLOOD_DAILY),
        "forecast_days": forecast_days,
        "timezone": TZ,
    }
    return fetch(session, FLOOD_URL, params)


def pull_flood_range(session, start: date, end: date) -> dict:
    """Date-windowed call — the flood-API equivalent of 'pagination'."""
    params = {
        "latitude": LAT,
        "longitude": LON,
        "daily": ",".join(FLOOD_DAILY),
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "timezone": TZ,
    }
    return fetch(session, FLOOD_URL, params)


# ---------- Saving ----------
def save_raw(name: str, payload: dict) -> Path:
    """Timestamped raw extract. Never overwrites — replayable."""
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = RAW_DIR / f"{name}_{ts}.json"
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    log.info("Saved %s", path)
    return path


# ---------- Backfill loop (repeated calls) ----------
def backfill_flood(session, start: date, end: date, chunk_days: int = 90):
    """Loop date windows because flood API caps long ranges."""
    cursor = start
    while cursor < end:
        chunk_end = min(cursor + timedelta(days=chunk_days), end)
        try:
            payload = pull_flood_range(session, cursor, chunk_end)
            save_raw(f"flood_{cursor}_{chunk_end}", payload)
        except requests.HTTPError as e:
            log.warning("Skipping %s→%s: %s", cursor, chunk_end, e)
        cursor = chunk_end + timedelta(days=1)
        time.sleep(1)  # polite pacing — respects free-tier rate limits


# ---------- Entry point ----------
def main():
    session = build_session()

    save_raw("weather_forecast", pull_weather(session))
    save_raw("flood_forecast", pull_flood_forecast(session))

    # Uncomment when you're ready to backfill history:
    # backfill_flood(session, date(2024, 1, 1), date(2026, 6, 1))


if __name__ == "__main__":
    main()
