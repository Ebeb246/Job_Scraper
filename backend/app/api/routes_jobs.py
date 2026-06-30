from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.jobs import get_jobs
from app.schemas.job import JobList, JobRead

router = APIRouter(tags=["jobs"])


@router.get("/jobs", response_model=JobList)
def read_jobs(
    db: Annotated[Session, Depends(get_db)],
    keyword: Annotated[str | None, Query()] = None,
    company: Annotated[str | None, Query()] = None,
) -> JobList:
    """Return stored jobs, optionally filtered by ?keyword= and/or ?company=."""
    jobs = get_jobs(db=db, keyword=keyword, company=company)
    return JobList(count=len(jobs), items=[JobRead.model_validate(job) for job in jobs])
