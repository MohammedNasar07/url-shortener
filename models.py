# models.py
from sqlalchemy import String, Integer, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from database import Base


class URL(Base):
    __tablename__ = "urls"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    original_url: Mapped[str] = mapped_column(String(2048), nullable=False, index=True)
    short_code: Mapped[str] = mapped_column(
        String(16), unique=True, index=True, nullable=False
    )
    created_at: Mapped["DateTime"] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    click_count: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="0"
    )
