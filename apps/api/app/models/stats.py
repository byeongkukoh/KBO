from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class TeamGameStat(Base):
    __tablename__ = "team_game_stats"
    __table_args__ = (UniqueConstraint("game_id", "team_id", name="uq_team_game_stats_game_team"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id", ondelete="CASCADE"), nullable=False, index=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id", ondelete="RESTRICT"), nullable=False, index=True)
    runs: Mapped[int] = mapped_column(Integer, nullable=False)
    hits: Mapped[int] = mapped_column(Integer, nullable=False)
    errors: Mapped[int] = mapped_column(Integer, nullable=False)
    walks: Mapped[int] = mapped_column(Integer, nullable=False)

    game = relationship("Game", back_populates="team_game_stats")
    team = relationship("Team")


class PlayerGameBattingStat(Base):
    __tablename__ = "player_game_batting_stats"
    __table_args__ = (UniqueConstraint("game_id", "team_id", "player_key", name="uq_player_batting_game_team_player"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id", ondelete="CASCADE"), nullable=False, index=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id", ondelete="RESTRICT"), nullable=False, index=True)
    player_key: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    player_name: Mapped[str] = mapped_column(String(64), nullable=False)
    batting_order: Mapped[int] = mapped_column(Integer, nullable=False)
    position_code: Mapped[str] = mapped_column(String(16), nullable=False)
    plate_appearances: Mapped[int] = mapped_column(Integer, nullable=False)
    at_bats: Mapped[int] = mapped_column(Integer, nullable=False)
    runs: Mapped[int] = mapped_column(Integer, nullable=False)
    hits: Mapped[int] = mapped_column(Integer, nullable=False)
    doubles: Mapped[int] = mapped_column(Integer, nullable=False)
    triples: Mapped[int] = mapped_column(Integer, nullable=False)
    home_runs: Mapped[int] = mapped_column(Integer, nullable=False)
    runs_batted_in: Mapped[int] = mapped_column(Integer, nullable=False)
    walks: Mapped[int] = mapped_column(Integer, nullable=False)
    hit_by_pitch: Mapped[int] = mapped_column(Integer, nullable=False)
    sacrifice_flies: Mapped[int] = mapped_column(Integer, nullable=False)
    strikeouts: Mapped[int] = mapped_column(Integer, nullable=False)

    game = relationship("Game", back_populates="player_batting_stats")
    team = relationship("Team")


class PlayerGamePitchingStat(Base):
    __tablename__ = "player_game_pitching_stats"
    __table_args__ = (UniqueConstraint("game_id", "team_id", "player_key", name="uq_player_pitching_game_team_player"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id", ondelete="CASCADE"), nullable=False, index=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id", ondelete="RESTRICT"), nullable=False, index=True)
    player_key: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    player_name: Mapped[str] = mapped_column(String(64), nullable=False)
    innings_outs: Mapped[int] = mapped_column(Integer, nullable=False)
    batters_faced: Mapped[int] = mapped_column(Integer, nullable=False)
    pitches_thrown: Mapped[int] = mapped_column(Integer, nullable=False)
    at_bats: Mapped[int] = mapped_column(Integer, nullable=False)
    hits_allowed: Mapped[int] = mapped_column(Integer, nullable=False)
    home_runs_allowed: Mapped[int] = mapped_column(Integer, nullable=False)
    walks_allowed: Mapped[int] = mapped_column(Integer, nullable=False)
    strikeouts: Mapped[int] = mapped_column(Integer, nullable=False)
    runs_allowed: Mapped[int] = mapped_column(Integer, nullable=False)
    earned_runs: Mapped[int] = mapped_column(Integer, nullable=False)

    game = relationship("Game", back_populates="player_pitching_stats")
    team = relationship("Team")
