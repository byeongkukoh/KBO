from math import ceil

from sqlalchemy import Select, and_, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models import Game, TeamGameStat


def list_games(session: Session, season: int, series_code: str | None, team_code: str | None, game_date: str | None, page: int, page_size: int) -> dict[str, object]:
    stmt: Select[tuple[Game]] = (
        select(Game)
        .options(selectinload(Game.away_team), selectinload(Game.home_team), selectinload(Game.team_game_stats).selectinload(TeamGameStat.team))
        .where(Game.season_id == season)
        .order_by(Game.game_date.desc(), Game.kbo_game_id.desc())
    )
    if series_code is not None:
        stmt = stmt.where(Game.series_code == series_code)
    if game_date is not None:
        stmt = stmt.where(Game.game_date == game_date)
    games = list(session.execute(stmt).scalars())
    if team_code is not None:
      games = [game for game in games if game.away_team.team_code == team_code or game.home_team.team_code == team_code]
    total_count = len(games)
    total_pages = max(1, ceil(total_count / page_size)) if total_count else 1
    current_page = min(max(page, 1), total_pages)
    page_games = games[(current_page - 1) * page_size : current_page * page_size]

    return {
        "season": season,
        "series_code": series_code,
        "team_code": team_code,
        "game_date": game_date,
        "page": current_page,
        "page_size": page_size,
        "total_count": total_count,
        "total_pages": total_pages,
        "items": [
            {
                "game_id": game.kbo_game_id,
                "game_date": game.game_date.isoformat(),
                "series_code": game.series_code,
                "series_name": game.series_name,
                "stadium": game.stadium,
                "away_team_code": game.away_team.team_code,
                "home_team_code": game.home_team.team_code,
                "away_score": game.away_score,
                "home_score": game.home_score,
                "status_code": game.status_code,
            }
            for game in page_games
        ],
    }
