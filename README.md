# Flood-Risk and Weather Monitoring for Noveleta, Cavite
**Program:** Data Engineering Pilipinas — Open Track (Cohort 1)  

**Builder:** Reiner John Santiago

**Timeline:** June 2026 – December 2026 (24 weeks)



## Problem Statement
Residents of Noveleta needs an accessible way to identify areas that are highly susceptible to flooding, including locations that may experience flooding even during light or moderate rainfall.

The dashboard aims to answer:

Which locations are most flood-prone, and how likely are they to experience flooding based on current and forecasted rainfall?

## Audience
• Residents of Noveleta, Cavite

• Local government units

• Disaster risk reduction and emergency-response teams

• Commuters and motorists

## KPI or Key Metric
The dashboard will monitor:

• Current rainfall: millimetres per hour

• Forecasted rainfall: expected rainfall for the next 24 hours

• Rain probability: percentage chance of rain

• Flood susceptibility level: Low, Moderate, High or Critical

• Number of flood-prone locations

• Estimated population or communities exposed

• Active weather or flood alerts

• Data last updated

• Distance to evacuation centres, when data is available

## Likely Data Source

**Primary Source**

Name: Open-Meteo Weather API & Flood API

**URL:**

Weather: https://api.open-meteo.com/v1/forecast

Flood: https://flood-api.open-meteo.com/v1/flood

Documentation: https://open-meteo.com/

Format: JSON (also supports CSV via parameter)

**Coverage:**

Weather: Global coverage, hourly/daily forecasts up to 16 days, historical data back to 1940 (ERA5 reanalysis), 80+ years of historical archive 

Flood: Simulated river discharge at 5 km resolution, available from 1984 up to 7 months forecast 

Target Location: Noveleta, Cavite is at approximately 14.4275°N, 120.8808°E with an elevation of ~9 meters above sea level 

Why it fits the problem: Provides free, no-API-key-required access to both real-time weather data (precipitation, temperature, wind) and flood forecasting (river discharge data) for any global location . Flood API specifically offers river discharge variables including mean, max, min, and percentile data, which directly supports flood-risk monitoring .

**Known limitations:**

Flood API uses simulated river discharge models (5 km resolution), not local gauge measurements

Commercial use requires an API key and subscription 

Data is model-derived, not from physical weather stations in Noveleta itself

Non-commercial use is free but requires attribution (CC BY 4.0) 

**Fallback Source**

Name: PAGASA ClimDatPh Platform

URL: https://bagong.pagasa.dost.gov.ph/climate/climate-data

Format: CSV (machine-readable)

Coverage: Daily, monthly, and annual climate data from 55 synoptic stations in the Philippines, with data available from as early as 1949 . The nearest PAGASA station to Noveleta would provide official observational data.

Why it could still work: Provides official, ground-truthed climate data from the Philippine government's weather agency, which is locally relevant and authoritative. Includes variables like rainfall, temperature, wind speed/direction, and relative humidity .

**Known limitations:**

Request-based system requiring formal application via Google Forms with 3+ working days processing time 

Sub-daily data may not always be available 

Data is delayed by approximately one year ("present" means one year behind current year) 

No direct flood API or real-time discharge data—only climate variables

No API for automated system integration; data is emailed manually

Requires validation documents (valid ID, research papers if applicable) for access 

## Possible Final Dashboard

• A map of flood-prone areas

• Current and forecasted rainfall

• Risk level for each monitored location

• Active weather advisories

• Locations that may become flooded

• Nearby evacuation centres and safer routes

• A clear status indicator: Normal, Alert, Warning or Critical

Purpose of dashboard:

The dashboard will help residents and authorities prepare for storms, monsoon rains and recurring flooding. It will support earlier decision-making, safer travel planning and faster emergency preparation.



## First Pull Path
- README.md
- scripts/ingest.py
- notebooks/flood_risk_analysis.ipynb
