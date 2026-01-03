# schemas.py
from pydantic import BaseModel, HttpUrl, field_validator


class ShortenRequest(BaseModel):
    original_url: HttpUrl

    @field_validator("original_url")
    @classmethod
    def url_length_check(cls, v):
        url_str = str(v)
        if len(url_str) > 2048:
            raise ValueError("URL too long (max 2048 characters)")
        return v


class ShortenResponse(BaseModel):
    short_code: str
    short_url: str
    original_url: str


class URLStats(BaseModel):
    short_code: str
    original_url: str
    click_count: int
    created_at: str


class HealthResponse(BaseModel):
    status: str
    database: str
    redis: str


class CacheStatsResponse(BaseModel):
    cache_hits: int
    cache_misses: int
    hit_rate: str
    total_requests: int
