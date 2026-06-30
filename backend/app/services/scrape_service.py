"""Orchestrates one scrape run: fetch from source, parse, store new jobs."""

from sqlalchemy.orm import Session

from app.repositories.jobs import insert_new_jobs
from app.schemas.scrape import ScrapeResult
from app.scraper import fetch_raw_jobs, parse_jobs


def run_scrape(db: Session) -> ScrapeResult:
    """Fetch jobs, store the new ones, and report counts.

    Raises httpx.HTTPError if source is unreachable.
    """
    raw_jobs = fetch_raw_jobs()
    parsed = parse_jobs(raw_jobs)
    inserted, skipped = insert_new_jobs(db, parsed)
    return ScrapeResult(fetched=len(parsed), inserted=inserted, skipped=skipped)
