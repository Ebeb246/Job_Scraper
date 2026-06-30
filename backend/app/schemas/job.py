from datetime import datetime

from pydantic import BaseModel, ConfigDict


class JobRead(BaseModel):
    """A job listing as returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    company: str
    location: str | None
    tags: list[str]
    date_posted: datetime | None
    url: str


class JobList(BaseModel):
    count: int
    items: list[JobRead]
