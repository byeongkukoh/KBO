from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Game(Base):
    __tablename__ = "games"

    id: Mapped[int] = mapped_column(primary_key=True)
    kbo_game_id: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    game_date: Mapped[date] = mapped_column(Date, nullable=False)
    status_code: Mapped[str] = mapped_column(String(16), nullable=False)
    stadium: Mapped[str] = mapped_column(String(128), nullable=False)
    season_id: Mapped[int] = mapped_column(Integer, nullable=False)
    le_id: Mapped[int] = mapped_column(Integer, nullable=False)
    sr_id: Mapped[int] = mapped_column(Integer, nullable=False)
    away_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id", ondelete="RESTRICT"), nullable=False)
    home_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id", ondelete="RESTRICT"), nullable=False)
    away_score: Mapped[int] = mapped_column(Integer, nullable=False)
    home_score: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    away_team = relationship("Team", back_populates="away_games", foreign_keys=[away_team_id])
    home_team = relationship("Team", back_populates="home_games", foreign_keys=[home_team_id])
    inning_scores = relationship("InningScore", back_populates="game", cascade="all, delete-orphan")
    team_game_stats = relationship("TeamGameStat", back_populates="game", cascade="all, delete-orphan")
    player_batting_stats = relationship("PlayerGameBattingStat", back_populates="game", cascade="all, delete-orphan")
    player_pitching_stats = relationship("PlayerGamePitchingStat", back_populates="game", cascade="all, delete-orphan")
    source_pages = relationship("GameSourcePage", back_populates="game", cascade="all, delete-orphan")


class InningScore(Base):
    __tablename__ = "inning_scores"
    __table_args__ = (UniqueConstraint("game_id", "inning_no", name="uq_inning_scores_game_inning"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id", ondelete="CASCADE"), nullable=False, index=True)
    inning_no: Mapped[int] = mapped_column(Integer, nullable=False)
    away_runs: Mapped[int] = mapped_column(Integer, nullable=False)
    home_runs: Mapped[int] = mapped_column(Integer, nullable=False)

    game = relationship("Game", back_populates="inning_scores")


class GameSourcePage(Base):
    __tablename__ = "game_source_pages"

    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id", ondelete="CASCADE"), nullable=False, index=True)
    source_type: Mapped[str] = mapped_column(String(32), nullable=False)
    source_url: Mapped[str] = mapped_column(Text, nullable=False)
    parser_version: Mapped[str] = mapped_column(String(32), nullable=False)
    checksum: Mapped[str] = mapped_column(String(128), nullable=False)
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    game = relationship("Game", back_populates="source_pages")
