from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class DataSyncRun(Base):
    __tablename__ = "data_sync_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    game_date: Mapped[str] = mapped_column(String(8), nullable=False)
    game_id: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    items = relationship("DataSyncItem", back_populates="run", cascade="all, delete-orphan")


class DataSyncItem(Base):
    __tablename__ = "data_sync_items"
    __table_args__ = (UniqueConstraint("run_id", "source_type", "external_key", name="uq_sync_item_run_source_key"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("data_sync_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    source_type: Mapped[str] = mapped_column(String(32), nullable=False)
    external_key: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    run = relationship("DataSyncRun", back_populates="items")
