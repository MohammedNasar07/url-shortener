# main.py
# The main FastAPI app with endpoints.

import os
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from database import engine, Base, get_db
from models import URL
from utils import encode_base62, validate_code
from schemas import ShortenRequest, ShortenResponse, URLStats

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(title="URL Shortener", version="1.0")

# Create tables in database if they don’t exist
Base.metadata.create_all(bind=engine)

# Read BASE_URL from .env (default = localhost)
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")


@app.get("/")
def home():
    return {"message": "URL Shortener API", "version": "1.0"}


# POST /shorten → create short URL
@app.post(
    "/shorten", response_model=ShortenResponse, status_code=status.HTTP_201_CREATED
)
def shorten(payload: ShortenRequest, db: Session = Depends(get_db)):
    original = str(payload.original_url)

    # Check if already shortened
    existing = db.query(URL).filter(URL.original_url == original).first()
    if existing:
        return {
            "short_code": existing.short_code,
            "short_url": f"{BASE_URL}/{existing.short_code}",
            "original_url": existing.original_url,
        }

    # Create new row
    row = URL(original_url=original, short_code="temp")
    db.add(row)
    db.commit()
    db.refresh(row)

    # Generate short code from ID
    code = encode_base62(row.id)
    row.short_code = code
    db.commit()

    return {
        "short_code": code,
        "short_url": f"{BASE_URL}/{code}",
        "original_url": original,
    }


# GET /{code} → redirect to original URL
@app.get("/{code}")
def redirect(code: str, db: Session = Depends(get_db)):
    if not validate_code(code):
        raise HTTPException(status_code=400, detail="Invalid code format")

    row = db.query(URL).filter(URL.short_code == code).first()
    if not row:
        raise HTTPException(status_code=404, detail="Not found")

    # Increment click count
    row.click_count += 1
    db.commit()

    # Redirect to original URL
    return RedirectResponse(url=row.original_url, status_code=302)


# GET /stats/{code} → show stats
@app.get("/stats/{code}", response_model=URLStats)
def stats(code: str, db: Session = Depends(get_db)):
    row = db.query(URL).filter(URL.short_code == code).first()
    if not row:
        raise HTTPException(status_code=404, detail="Not found")

    return {
        "short_code": row.short_code,
        "original_url": row.original_url,
        "click_count": row.click_count,
        "created_at": row.created_at.isoformat(),
    }
