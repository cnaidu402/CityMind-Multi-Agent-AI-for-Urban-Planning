# CityMind: Multi-Agent AI for Urban Planning

CityMind is a Maryland-only urban planning simulator that evaluates a proposed development site with multiple domain agents, live spatial data, and an LLM-based synthesis layer.

The current backend accepts a natural-language address and a project description, geocodes the site, runs a sequence of agent reviews, and returns a structured planning report through a Flask API and a Streamlit demo UI.

## What It Does

- Geocodes a Maryland address or area description
- Runs five planning reviews:
  - `Environmental`
  - `Safety`
  - `Transit`
  - `Infrastructure`
  - `ROI / Economic`
- Builds a structured debate record
- Produces a final decision and synthesis using OpenAI, with deterministic fallback logic

## Current Agent Stack

### 1. Environmental Agent
- Checks whether the site intersects Maryland Critical Area polygons using Maryland iMAP ArcGIS services

### 2. Safety Agent
- Reviews Baltimore Part 1 crime density within 500 meters over the last year

### 3. Transit Agent
- Calculates distance to the nearest seeded Maryland transit anchor

### 4. Infrastructure Agent
- Finds nearby hospitals from Maryland iMAP
- Finds nearby grocery access using OpenStreetMap Overpass
- Falls back to safe mock values if live infrastructure APIs fail

### 5. ROI / Economic Agent
- Uses seeded Maryland market reference points for rent and appreciation estimates

## LLM Provider

The project is currently configured to use the OpenAI API for final debate orchestration and synthesis.

Default model:

- `gpt-4.1`

## Project Structure

```text
e:\Hackathon_UMBC/
├─ data/
├─ notebooks/
├─ src/
│  └─ maryland_planning_simulator/
│     ├─ agents/
│     ├─ api/
│     ├─ graphs/
│     ├─ schemas/
│     ├─ services/
│     ├─ tools/
│     ├─ api_server.py
│     ├─ main.py
│     ├─ settings.py
│     └─ streamlit_app.py
├─ tests/
├─ .env.example
├─ .gitignore
└─ requirements.txt
```

## Setup

### 1. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 2. Configure environment variables

Create a repo-root `.env` file:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4.1
```

A template is already included in [.env.example](./.env.example).

## Run the Backend

From the repo root:

```powershell
$env:PYTHONPATH="e:\Hackathon_UMBC\src"
python -m maryland_planning_simulator.api_server
```

Health endpoint:

```text
http://127.0.0.1:5000/health
```

## Run the Streamlit Demo

In a second terminal:

```powershell
$env:PYTHONPATH="e:\Hackathon_UMBC\src"
streamlit run src/maryland_planning_simulator/streamlit_app.py
```

UI:

```text
http://127.0.0.1:8501
```

## Flask API

### `GET /health`

Returns a simple service-health payload.

### `POST /simulate`

Request body:

```json
{
  "address": "100 State Circle, Annapolis, MD",
  "project_description": "300-unit mixed-use apartment complex with ground-floor retail"
}
```

Response shape:

```json
{
  "approved": false,
  "project": {},
  "coordinates": {},
  "assessments": [],
  "debate": {},
  "final_synthesis": "Final decision: Not approved. ...",
  "synthesis_provider": "openai",
  "synthesis_model": "gpt-4.1",
  "synthesis_error": null,
  "generated_at_utc": "..."
}
```

## Tests

Run the test suite:

```bash
python -m unittest tests.test_api tests.test_planning_graph tests.test_orchestrator -v
```

## Current Limitations

- This is intentionally scoped to Maryland
- The safety tool currently depends on Baltimore City open data, so non-Baltimore sites may trigger manual-review behavior
- Transit and economic reviews currently use seeded reference data, not full live statewide feeds
- Infrastructure review includes fallback values when external services time out
- The final decision is deterministic, while the narrative synthesis is LLM-generated but constrained to match that decision

## Roadmap

- Replace seeded transit data with live GTFS or statewide stop data
- Replace seeded economic signals with a live real-estate data provider
- Improve non-Baltimore safety coverage
- Add map visualization with Folium or Leaflet
- Add Docker support and deployment configuration

## Security Notes

- Do not commit `.env`
- If an API key was ever pasted into chat or logs, rotate it and replace it locally

## Status

This repo currently contains:

- working multi-agent backend
- Flask API
- Streamlit demo
- OpenAI-backed synthesis
- test coverage for the core orchestration path
