from pydantic import BaseModel


class ScrapeResult(BaseModel):
    """Summary of a single scrape run."""

    fetched: int  # jobs returned by the source
    inserted: int  # new jobs written to the DB
    skipped: int  # jobs already present (deduped)
