"""Scraper for the RemoteOK public JSON API."""

from datetime import datetime
from typing import Any

import httpx

from app.core.config import settings

# RemoteOK blocks requests without a browser-like User-Agent.
_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; JobScraper/1.0)"}
_TIMEOUT = 15.0


def fetch_raw_jobs() -> list[dict[str, Any]]:
    """
    Fetch the raw job list from the source.

    Raises httpx.HTTPError on failure.
    """
    response = httpx.get(settings.job_source_url, headers=_HEADERS, timeout=_TIMEOUT)
    response.raise_for_status()
    data = response.json()
    # Drop leading metadata element
    return [item for item in data[1:] if isinstance(item, dict)]


def parse_job(raw: dict[str, Any]) -> dict[str, Any] | None:
    """
    Map one raw RemoteOK entry to the needed fields.

    Returns None if required fields are missing.
    """
    remoteok_id = raw.get("id")
    title = raw.get("position")
    company = raw.get("company")
    url = raw.get("url")
    if not (remoteok_id and title and company and url):
        return None

    return {
        "remoteok_id": str(remoteok_id),
        "title": title.strip(),
        "company": company.strip(),
        "location": (raw.get("location") or "").strip() or None,
        "tags": [t for t in raw.get("tags", []) if isinstance(t, str)],
        "date_posted": _parse_date(raw.get("date")),
        "url": url,
    }


def parse_jobs(raw_jobs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Parse and clean a list of raw entries, dropping invalid ones."""
    parsed = [parse_job(raw) for raw in raw_jobs]
    return [job for job in parsed if job is not None]


def _parse_date(value: Any) -> datetime | None:
    """Parse api date to datetime. Returns None if invalid or missing."""
    if not isinstance(value, str):
        return None
    try:
        dt = datetime.fromisoformat(value)
    except ValueError:
        return None
    return dt.replace(tzinfo=None)
