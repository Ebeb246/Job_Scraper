# Job Listings Scraper & Dashboard

Scrapes remote job listings from the [RemoteOK](https://remoteok.com) public JSON
API, stores them in MySQL, serves them through a FastAPI REST API, and shows them
on a small Vue dashboard. Runs entirely with Docker Compose.

**Stack:** FastAPI + SQLAlchemy · MySQL 8 · Vue 3 + Vite · GitHub Actions CI

## Run it

Requires Docker. Two commands:

```bash
docker compose up --build
# then open http://localhost:8000
```

Starts MySQL, the API (host port 8001), and the dashboard (host port 8000,
proxying `/api` to the API). Tables are created on startup by the ORM — no
migration step.

## Trigger a scrape

The database starts empty. Fill it either way:

- **Dashboard:** click **Scrape now** (top right).
- **API:** `curl -X POST http://localhost:8000/api/scrape`

Each run pulls the latest ~100 jobs RemoteOK returns and stores any that are new.
Re-running is safe — jobs are deduplicated on the source's id.

## API

| Method | Endpoint  | Description |
|--------|-----------|-------------|
| `POST` | `/scrape` | Fetch from RemoteOK and store new jobs. Returns `{fetched, inserted, skipped}`. |
| `GET`  | `/jobs`   | All stored jobs. Filters: `?keyword=python`, `?company=stripe`. |
| `GET`  | `/stats`  | Totals: job count, top 5 tags, jobs per day. |

Interactive docs: http://localhost:8001/docs

## Dashboard

A single page showing the total jobs stored, a **top-skills bar chart**, and a
**filterable job table** (live keyword + company filters, each row links to the
posting). Click **Scrape now** to fetch fresh data.

## Project layout

```
backend/app/   api · services · repositories · models · schemas · scraper.py
frontend/      Vue 3 dashboard (src/App.vue, src/api.ts)
.github/       CI workflow (lint + tests on push/PR)
docker-compose.yml
```

## Notes

- RemoteOK's API returns a metadata notice as the first array element — the
  scraper skips it.
- Deduplication keys on RemoteOK's job id; a unique DB constraint is the safety net.
- Schema lives in the ORM models (created on startup), so there is no `schema.sql`.
- Tests: scraper unit tests (no DB) + a `/stats` integration test against MySQL.
