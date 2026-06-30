from datetime import datetime

from sqlalchemy import JSON, DateTime, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Job(Base):
    """A single job listing scraped from the source board."""

    __tablename__ = "jobs"

    # remoteok_id is the source's stable id; we dedupe on it across scrape runs.
    __table_args__ = (UniqueConstraint("remoteok_id", name="uq_jobs_remoteok_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    remoteok_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    company: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    tags: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    date_posted: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    url: Mapped[str] = mapped_column(String(500), nullable=False)

    # When our scraper stored this row (used for "jobs per day" stats).
    scraped_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"<Job title={self.title!r} company={self.company!r}>"
