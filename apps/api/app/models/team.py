from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Team(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(primary_key=True)
    team_code: Mapped[str] = mapped_column(String(8), unique=True, nullable=False, index=True)
    team_name: Mapped[str] = mapped_column(String(64), nullable=False)

    home_games = relationship("Game", back_populates="home_team", foreign_keys="Game.home_team_id")
    away_games = relationship("Game", back_populates="away_team", foreign_keys="Game.away_team_id")
