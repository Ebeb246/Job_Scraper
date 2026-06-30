from datetime import date

from pydantic import BaseModel


class TagCount(BaseModel):
    tag: str
    count: int


class DayCount(BaseModel):
    day: date
    count: int


class StatsResponse(BaseModel):
    total_jobs: int
    top_tags: list[TagCount]  # top 5 tags/skills by frequency
    jobs_per_day: list[DayCount]  # jobs grouped by posting date
