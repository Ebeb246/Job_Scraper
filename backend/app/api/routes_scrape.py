from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.scrape import ScrapeResult
from app.services.scrape_service import run_scrape

router = APIRouter(tags=["scrape"])


@router.post("/scrape", response_model=ScrapeResult)
def trigger_scrape(db: Annotated[Session, Depends(get_db)]) -> ScrapeResult:
    """Trigger a scrape run. Maps a source failure to HTTP 502."""
    try:
        return run_scrape(db)
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to fetch from job source: {e}",
        ) from e
