# main.py
import os
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from database import engine, Base, get_db
from models import URL
from utils import encode_base62, validate_code, get_redis, CacheStats
from schemas import (
    ShortenRequest,
    ShortenResponse,
    URLStats,
    HealthResponse,
    CacheStatsResponse,
)

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="URL Shortener API",
    description="A fast URL shortener with Redis caching",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Create tables in database if they don't exist
Base.metadata.create_all(bind=engine)

# Read BASE_URL from .env
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

# Redis TTL (24 hours for popular URLs)
REDIS_TTL = 86400


@app.get("/")
def home():
    """API root endpoint"""
    return {
        "message": "URL Shortener API",
        "version": "1.0.0",
        "docs": f"{BASE_URL}/docs",
    }


@app.get("/health", response_model=HealthResponse)
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint for monitoring"""
    try:
        # Check database
        db.execute("SELECT 1")
        db_status = "connected"
    except SQLAlchemyError:
        db_status = "disconnected"

    # Check Redis
    redis_client = get_redis()
    redis_status = "connected" if redis_client else "disconnected"

    overall_status = "healthy" if (db_status == "connected") else "unhealthy"

    return {"status": overall_status, "database": db_status, "redis": redis_status}


@app.post(
    "/shorten", response_model=ShortenResponse, status_code=status.HTTP_201_CREATED
)
def shorten(payload: ShortenRequest, db: Session = Depends(get_db)):
    """Create a short URL from an original URL"""
    original = str(payload.original_url)

    # Check if URL already exists
    existing = db.query(URL).filter(URL.original_url == original).first()
    if existing:
        return {
            "short_code": existing.short_code,
            "short_url": f"{BASE_URL}/{existing.short_code}",
            "original_url": existing.original_url,
        }

    # Create new URL entry
    row = URL(original_url=original, short_code="temp")
    db.add(row)
    db.commit()
    db.refresh(row)

    # Generate short code from ID using base62
    code = encode_base62(row.id)
    row.short_code = code
    db.commit()

    # Proactively cache the new URL
    redis_client = get_redis()
    if redis_client:
        try:
            redis_client.setex(code, REDIS_TTL, original)
        except Exception:
            pass  # Continue even if caching fails

    return {
        "short_code": code,
        "short_url": f"{BASE_URL}/{code}",
        "original_url": original,
    }


@app.get("/{code}")
def redirect(code: str, db: Session = Depends(get_db)):
    """Redirect short code to original URL (with Redis caching)"""

    # Validate code format
    if not validate_code(code):
        raise HTTPException(status_code=400, detail="Invalid short code format")

    redis_client = get_redis()

    # Try Redis cache first
    if redis_client:
        try:
            cached_url = redis_client.get(code)
            if cached_url:
                CacheStats.record_hit()
                return RedirectResponse(url=cached_url, status_code=302)
        except Exception:
            pass  # Fall through to database on Redis error

    # Cache miss - query database
    CacheStats.record_miss()
    row = db.query(URL).filter(URL.short_code == code).first()

    if not row:
        raise HTTPException(status_code=404, detail="Short URL not found")

    # Increment click count
    row.click_count += 1
    db.commit()

    # Update Redis cache
    if redis_client:
        try:
            redis_client.setex(code, REDIS_TTL, row.original_url)
        except Exception:
            pass  # Continue even if caching fails

    return RedirectResponse(url=row.original_url, status_code=302)


@app.get("/stats/{code}", response_model=URLStats)
def stats(code: str, db: Session = Depends(get_db)):
    """Get statistics for a short URL"""
    row = db.query(URL).filter(URL.short_code == code).first()
    if not row:
        raise HTTPException(status_code=404, detail="Short URL not found")

    return {
        "short_code": row.short_code,
        "original_url": row.original_url,
        "click_count": row.click_count,
        "created_at": row.created_at.isoformat(),
    }


@app.get("/api/cache-stats", response_model=CacheStatsResponse)
def get_cache_stats():
    """Get Redis cache performance statistics"""
    return CacheStats.report()


@app.post("/api/cache-stats/reset")
def reset_cache_stats():
    """Reset cache statistics (useful for testing)"""
    CacheStats.reset()
    return {"message": "Cache statistics reset successfully"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
