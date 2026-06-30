from collections import Counter
from datetime import date
from typing import Any

from sqlalchemy import String, func, select
from sqlalchemy.orm import Session

from app.models.jobs import Job


def get_jobs(
    db: Session,
    keyword: str | None = None,
    company: str | None = None,
) -> list[Job]:
    """Return stored jobs, optionally filtered by keyword and/or company."""
    stmt = select(Job).order_by(Job.date_posted.desc())

    if keyword:
        like = f"%{keyword}%"
        # Match against the title or the (JSON) tags serialized to text.
        stmt = stmt.where(Job.title.ilike(like) | func.cast(Job.tags, String).ilike(like))
    if company:
        stmt = stmt.where(Job.company.ilike(f"%{company}%"))

    return list(db.execute(stmt).scalars().all())


def insert_new_jobs(db: Session, parsed_jobs: list[dict[str, Any]]) -> tuple[int, int]:
    """Insert only jobs not already stored. Returns (inserted, skipped)."""
    by_id = {job["remoteok_id"]: job for job in parsed_jobs}

    existing_ids = set(db.execute(select(Job.remoteok_id)).scalars().all())
    new_jobs = [job for rid, job in by_id.items() if rid not in existing_ids]

    db.add_all([Job(**job) for job in new_jobs])
    db.commit()

    return len(new_jobs), len(parsed_jobs) - len(new_jobs)


def get_total_jobs(db: Session) -> int:
    return db.execute(select(func.count()).select_from(Job)).scalar_one()


def get_top_tags(db: Session, limit: int = 5) -> list[tuple[str, int]]:
    """Top tags by frequency."""
    all_tags = db.execute(select(Job.tags)).scalars().all()
    counter: Counter[str] = Counter()
    for tags in all_tags:
        counter.update(tags or [])
    return counter.most_common(limit)


def get_jobs_per_day(db: Session) -> list[tuple[date, int]]:
    """Count jobs grouped by posting date (ignores rows without a date)."""
    day = func.date(Job.date_posted)
    stmt = (
        select(day.label("day"), func.count().label("count"))
        .where(Job.date_posted.is_not(None))
        .group_by(day)
        .order_by(day)
    )
    return [(row.day, row.count) for row in db.execute(stmt)]
