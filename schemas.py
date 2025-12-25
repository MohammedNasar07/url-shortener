# schemas.py
# Defines input/output shapes for FastAPI endpoints.

from pydantic import BaseModel, HttpUrl


class ShortenRequest(BaseModel):
    original_url: HttpUrl  # Input must be a valid URL


class ShortenResponse(BaseModel):
    short_code: str
    short_url: str
    original_url: str


class URLStats(BaseModel):
    short_code: str
    original_url: str
    click_count: int
    created_at: str
