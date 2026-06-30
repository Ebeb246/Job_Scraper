from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.jobs import get_jobs_per_day, get_top_tags, get_total_jobs
from app.schemas.stats import DayCount, StatsResponse, TagCount

router = APIRouter(tags=["stats"])


@router.get("/stats", response_model=StatsResponse)
def read_stats(db: Annotated[Session, Depends(get_db)]) -> StatsResponse:
    """Aggregate stats: total jobs, top 5 tags, and jobs per day."""
    return StatsResponse(
        total_jobs=get_total_jobs(db),
        top_tags=[TagCount(tag=tag, count=count) for tag, count in get_top_tags(db)],
        jobs_per_day=[DayCount(day=day, count=count) for day, count in get_jobs_per_day(db)],
    )
