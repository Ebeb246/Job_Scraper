"""Unit tests for the scraper's pure functions (no DB, no network)."""

from datetime import datetime

import httpx

from app import scraper
from app.scraper import _parse_date, fetch_raw_jobs, parse_job, parse_jobs


def _raw_job(**overrides):
    base = {
        "id": 123,
        "position": "Backend Engineer",
        "company": "Acme",
        "location": "Remote",
        "tags": ["python", "api"],
        "date": "2026-06-29T20:03:38+00:00",
        "url": "https://remoteok.com/remote-jobs/123",
    }
    base.update(overrides)
    return base


def test_parse_job_maps_fields():
    result = parse_job(_raw_job())
    assert result == {
        "remoteok_id": "123",
        "title": "Backend Engineer",
        "company": "Acme",
        "location": "Remote",
        "tags": ["python", "api"],
        "date_posted": datetime(2026, 6, 29, 20, 3, 38),
        "url": "https://remoteok.com/remote-jobs/123",
    }


def test_parse_job_missing_required_field_returns_none():
    assert parse_job(_raw_job(company=None)) is None
    assert parse_job(_raw_job(url=None)) is None
    assert parse_job(_raw_job(position="")) is None


def test_parse_job_empty_location_becomes_none():
    result = parse_job(_raw_job(location=""))
    assert result is not None
    assert result["location"] is None


def test_parse_job_filters_non_string_tags():
    result = parse_job(_raw_job(tags=["python", 42, None, "api"]))
    assert result is not None
    assert result["tags"] == ["python", "api"]


def test_parse_date_variants():
    assert _parse_date("2026-06-29T20:03:38+00:00") == datetime(2026, 6, 29, 20, 3, 38)
    assert _parse_date("not-a-date") is None
    assert _parse_date(None) is None
    assert _parse_date(1234567890) is None


def test_parse_jobs_drops_invalid_entries():
    raw = [_raw_job(id=1), _raw_job(id=2, company=None), _raw_job(id=3)]
    result = parse_jobs(raw)
    assert [job["remoteok_id"] for job in result] == ["1", "3"]


def test_fetch_raw_jobs_drops_metadata_row(monkeypatch):
    # RemoteOK returns the legal/metadata notice as the first element.
    payload = [
        {"legal": "RemoteOK API notice"},  # index 0 — must be dropped
        _raw_job(id=1),
        "junk-not-a-dict",  # must be filtered out
        _raw_job(id=2),
    ]

    def fake_get(url, headers=None, timeout=None):
        return httpx.Response(200, json=payload, request=httpx.Request("GET", url))

    monkeypatch.setattr(scraper.httpx, "get", fake_get)

    result = fetch_raw_jobs()
    assert [job["id"] for job in result] == [1, 2]
