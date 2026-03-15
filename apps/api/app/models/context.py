from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class LeagueSeasonBattingContext(Base):
    __tablename__ = "league_season_batting_contexts"
    __table_args__ = (UniqueConstraint("season_id", "series_code", name="uq_league_batting_context_season_series"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    season_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    series_code: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    plate_appearances: Mapped[int] = mapped_column(Integer, nullable=False)
    at_bats: Mapped[int] = mapped_column(Integer, nullable=False)
    hits: Mapped[int] = mapped_column(Integer, nullable=False)
    doubles: Mapped[int] = mapped_column(Integer, nullable=False)
    triples: Mapped[int] = mapped_column(Integer, nullable=False)
    home_runs: Mapped[int] = mapped_column(Integer, nullable=False)
    stolen_bases: Mapped[int] = mapped_column(Integer, nullable=False)
    strikeouts: Mapped[int] = mapped_column(Integer, nullable=False)
    walks: Mapped[int] = mapped_column(Integer, nullable=False)
    hit_by_pitch: Mapped[int] = mapped_column(Integer, nullable=False)
    sacrifice_flies: Mapped[int] = mapped_column(Integer, nullable=False)
    runs_scored: Mapped[int] = mapped_column(Integer, nullable=False)
    batting_avg: Mapped[float | None] = mapped_column(Float, nullable=True)
    obp: Mapped[float | None] = mapped_column(Float, nullable=True)
    slg: Mapped[float | None] = mapped_column(Float, nullable=True)
    ops: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class LeagueSeasonPitchingContext(Base):
    __tablename__ = "league_season_pitching_contexts"
    __table_args__ = (UniqueConstraint("season_id", "series_code", name="uq_league_pitching_context_season_series"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    season_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    series_code: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    innings_outs: Mapped[int] = mapped_column(Integer, nullable=False)
    hits_allowed: Mapped[int] = mapped_column(Integer, nullable=False)
    walks_allowed: Mapped[int] = mapped_column(Integer, nullable=False)
    hit_by_pitch_allowed: Mapped[int] = mapped_column(Integer, nullable=False)
    strikeouts: Mapped[int] = mapped_column(Integer, nullable=False)
    earned_runs: Mapped[int] = mapped_column(Integer, nullable=False)
    era: Mapped[float | None] = mapped_column(Float, nullable=True)
    whip: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class AdvancedMetricConstant(Base):
    __tablename__ = "advanced_metric_constants"
    __table_args__ = (UniqueConstraint("season_id", "series_code", "metric_code", name="uq_metric_constant_season_series_metric"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    season_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    series_code: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    metric_code: Mapped[str] = mapped_column(String(64), nullable=False)
    metric_value: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
