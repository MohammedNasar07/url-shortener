# database.py
# This file connects FastAPI to PostgreSQL using SQLAlchemy.

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# Load environment variables from .env file
load_dotenv()

# Read the DATABASE_URL from .env
DATABASE_URL = os.getenv("DATABASE_URL")

# Create an engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Verify connections before use
    echo=False,  # Set to True for SQL logging during development
)

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
