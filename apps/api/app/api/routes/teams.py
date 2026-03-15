from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.team_detail import TeamRecentGameResponse, TeamSeasonDetailResponse
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
    return TeamSeasonDetailResponse(
        season=int(detail["season"]),
        series_code=detail["series_code"],
        team_code=str(detail["team_code"]),
        team_name=str(detail["team_name"]),
        wins=int(detail["wins"]),
        losses=int(detail["losses"]),
        draws=int(detail["draws"]),
        win_pct=detail["win_pct"],
        runs_scored=int(detail["runs_scored"]),
        runs_allowed=int(detail["runs_allowed"]),
        run_diff=int(detail["run_diff"]),
        hits=int(detail["hits"]),
        doubles=int(detail["doubles"]),
        stolen_bases=int(detail["stolen_bases"]),
        batting_avg=detail["batting_avg"],
        ops=detail["ops"],
        era=detail["era"],
        whip=detail["whip"],
        ops_plus=detail["ops_plus"],
        era_plus=detail["era_plus"],
        last_ten=str(detail["last_ten"]),
        streak=str(detail["streak"]),
        recent_games=[TeamRecentGameResponse(**item) for item in detail["recent_games"]],
    )
