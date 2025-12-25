# models.py
# This file defines the "urls" table in PostgreSQL.

from sqlalchemy import String, Integer, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from database import Base


class URL(Base):
    __tablename__ = "urls"  # Table name in PostgreSQL

    # Auto-increment ID (1, 2, 3...)
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Original long URL
    original_url: Mapped[str] = mapped_column(String(2048), nullable=False)

    # Short code (like "aB7kQ"), must be unique
    short_code: Mapped[str] = mapped_column(
        String(16), unique=True, index=True, nullable=False
    )

    # Timestamp when created
    created_at: Mapped["DateTime"] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Count how many times people clicked
    click_count: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="0"
    )
