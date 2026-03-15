from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import DataSyncRun, Game, LeagueSeasonBattingContext, LeagueSeasonPitchingContext


def get_scope_freshness(session: Session, season: int | None = None, series_code: str | None = None) -> dict[str, str | None]:
    game_stmt = select(func.max(Game.game_date))
    if season is not None:
        game_stmt = game_stmt.where(Game.season_id == season)
    if series_code is not None:
        game_stmt = game_stmt.where(Game.series_code == series_code)
    latest_game_date = session.execute(game_stmt).scalar_one_or_none()

    sync_stmt = select(func.max(DataSyncRun.finished_at)).where(DataSyncRun.status == "success")
    last_sync = session.execute(sync_stmt).scalar_one_or_none()

    context_stmt = select(func.max(LeagueSeasonBattingContext.updated_at))
    if season is not None:
        context_stmt = context_stmt.where(LeagueSeasonBattingContext.season_id == season)
    if series_code is not None:
        context_stmt = context_stmt.where(LeagueSeasonBattingContext.series_code == series_code)
    batting_updated = session.execute(context_stmt).scalar_one_or_none()

    pitching_stmt = select(func.max(LeagueSeasonPitchingContext.updated_at))
    if season is not None:
        pitching_stmt = pitching_stmt.where(LeagueSeasonPitchingContext.season_id == season)
    if series_code is not None:
        pitching_stmt = pitching_stmt.where(LeagueSeasonPitchingContext.series_code == series_code)
    pitching_updated = session.execute(pitching_stmt).scalar_one_or_none()

    context_updated = max([value for value in [batting_updated, pitching_updated] if value is not None], default=None)

    return {
        "latest_game_date": latest_game_date.isoformat() if latest_game_date is not None else None,
        "last_successful_sync_at": last_sync.isoformat() if last_sync is not None else None,
        "context_updated_at": context_updated.isoformat() if context_updated is not None else None,
    }
