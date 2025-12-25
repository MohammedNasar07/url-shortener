# database.py
# This file connects FastAPI to PostgreSQL using SQLAlchemy.

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# Load environment variables from .env file
load_dotenv()

# Read the DATABASE_URL from .env (example: postgresql://user:password@localhost:5432/url_shortener)
DATABASE_URL = os.getenv("DATABASE_URL")

# Create an engine (bridge between Python and PostgreSQL)
engine = create_engine(DATABASE_URL)

# SessionLocal = our "pen" to write/read in the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Base = template for creating tables
class Base(DeclarativeBase):
    pass


# Dependency for FastAPI: gives a database session to each request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
