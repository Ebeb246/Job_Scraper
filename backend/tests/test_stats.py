"""Integration test for the /stats endpoint against a real MySQL database.

Requires DATABASE_URL to point at a running MySQL (compose locally, service
container in CI). The TestClient context manager runs the app lifespan, which
creates the tables. No SQLite involved.
"""

from fastapi.testclient import TestClient

from app.main import app


def test_stats_returns_expected_shape():
    with TestClient(app) as client:
        res = client.get("/stats")

    assert res.status_code == 200
    body = res.json()
    assert set(body.keys()) == {"total_jobs", "top_tags", "jobs_per_day"}
    assert isinstance(body["total_jobs"], int)
    assert isinstance(body["top_tags"], list)
    assert isinstance(body["jobs_per_day"], list)
