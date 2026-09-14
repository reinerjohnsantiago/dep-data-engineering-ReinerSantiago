# Flood-Risk and Weather Monitoring for Noveleta, Cavite

**Builder:** Reiner John Santiago
**Program:** Data Engineering Pilipinas — Open Track (Cohort 1)
**Timeline:** June 2026 – December 2026

## What problem I'm solving

Residents of Noveleta, Cavite need an accessible way to identify areas that are highly
susceptible to flooding, including locations that may flood even during light or moderate
rainfall. This project builds a data pipeline and dashboard that answers:

> Which locations are most flood-prone, and how likely are they to experience flooding
> based on current and forecasted rainfall?

**Audience:** Noveleta residents, local government units, DRRMO teams, commuters.

## Where my data comes from

- **Primary:** Open-Meteo Weather API & Flood API
  - Weather: https://api.open-meteo.com/v1/forecast
  - Flood: https://flood-api.open-meteo.com/v1/flood
  - Format: JSON
  - License: CC BY 4.0 — attribution required
  - Target: Noveleta, Cavite (14.4275°N, 120.8808°E)
- **Fallback:** PAGASA ClimDatPh (request-based, not automated)

See the [root README](../../README.md) for full source analysis and limitations.

## How to run my scripts

```bash
# Setup
cd cohorts/starter-kit
python -m venv .venv
# Windows:
.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate
pip install -r requirements.txt

# Ingestion (Phase 2)
python scripts/ingest.py
# Output: timestamped raw JSON in data/raw/
```

## Project structure

```
data/
  raw/          # untouched Open-Meteo responses (timestamped)
  processed/    # cleaned / transformed (Phase 3+)
scripts/
  ingest.py     # Open-Meteo ingestion
  transform.py  # transformation (Phase 3+)
notebooks/      # analysis (Phase 4+)
output/figures/ # charts and maps (Phase 4+)
dashboard/      # deployed dashboard (Phase 6)
```

## Milestones

| Milestone | When | Status |
|---|---|---|
| M0 — Repo public, README describes project | Week 1 | ✅ |
| M1 — Folder structure, requirements.txt | Week 3–4 | ✅ |
| M2 — `ingest.py` runs, `data/raw/` has real data | Week 6 | 🚧 in progress |
| M3 — `transform.py` runs, `data/processed/` has output | Week 12 | ⏳ |
| M4 — Notebook exists and runs end-to-end | Week 16 | ⏳ |
| M5 — Pipeline connected, path-specific outputs | Week 20 | ⏳ |
| M6 — Dashboard live at a public URL | Week 24 | ⏳ |

## Notes

- Scraping compliance: N/A — this project uses documented public APIs, not web scraping.
- Rate limiting respected via `urllib3.Retry` (429/5xx backoff).
- Data license: Open-Meteo CC BY 4.0 — attribution required in the dashboard footer.