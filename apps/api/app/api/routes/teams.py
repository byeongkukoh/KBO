from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Any, cast

from app.db.session import get_db
from app.schemas.freshness import FreshnessResponse
from app.schemas.team_detail import TeamRecentGameResponse, TeamSeasonDetailResponse
from app.services.freshness_service import get_scope_freshness
from app.services.team_detail_service import get_team_season_detail

router = APIRouter(tags=["teams"])


@router.get("/teams/{team_code}/season-detail", response_model=TeamSeasonDetailResponse)
def get_team_detail(
    team_code: str,
    season: int,
    series_code: str | None = Query(default=None, pattern="^(preseason|regular|postseason)$"),
    session: Session = Depends(get_db),
) -> TeamSeasonDetailResponse:
    detail = get_team_season_detail(session, season=season, team_code=team_code, series_code=series_code)
    if detail is None:
        raise HTTPException(status_code=404, detail="team not found")
    detail_data = cast(dict[str, Any], detail)
    freshness = get_scope_freshness(session, season=season, series_code=series_code)
    return TeamSeasonDetailResponse(
        season=int(detail_data["season"]),
        series_code=cast(str | None, detail_data["series_code"]),
        team_code=str(detail_data["team_code"]),
        team_name=str(detail_data["team_name"]),
        wins=int(detail_data["wins"]),
        losses=int(detail_data["losses"]),
        draws=int(detail_data["draws"]),
        win_pct=cast(float | None, detail_data["win_pct"]),
        runs_scored=int(detail_data["runs_scored"]),
        runs_allowed=int(detail_data["runs_allowed"]),
        run_diff=int(detail_data["run_diff"]),
        hits=int(detail_data["hits"]),
        doubles=int(detail_data["doubles"]),
        stolen_bases=int(detail_data["stolen_bases"]),
        batting_avg=cast(float | None, detail_data["batting_avg"]),
        ops=cast(float | None, detail_data["ops"]),
        era=cast(float | None, detail_data["era"]),
        whip=cast(float | None, detail_data["whip"]),
        ops_plus=cast(float | None, detail_data["ops_plus"]),
        era_plus=cast(float | None, detail_data["era_plus"]),
        last_ten=str(detail_data["last_ten"]),
        streak=str(detail_data["streak"]),
        freshness=FreshnessResponse(**freshness),
        recent_games=[TeamRecentGameResponse(**cast(dict[str, Any], item)) for item in cast(list[dict[str, Any]], detail_data["recent_games"])],
    )
