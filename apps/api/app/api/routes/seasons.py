from dataclasses import asdict

from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.season_center_query_service import list_available_seasons, get_season_center_snapshot

router = APIRouter(tags=["seasons"])


class SeasonListResponse(BaseModel):
    seasons: list[int]


class TeamStandingResponse(BaseModel):
    rank: int
    games: int
    team_code: str
    team_name: str
    wins: int
    losses: int
    draws: int
    win_pct: float
    games_back: float
    runs_scored: int
    runs_allowed: int
    run_diff: int
    hits: int
    doubles: int
    batting_avg: float | None
    obp: float | None
    slg: float | None
    ops: float | None
    home_runs: int
    stolen_bases: int | None
    era: float | None
    whip: float | None
    last_ten: str
    streak: str


class LeaderboardPlayerResponse(BaseModel):
    player_id: str
    player_name: str
    team_code: str
    games: int
    plate_appearances: int | None
    innings: float | None
    batting_avg: float | None
    hits: int | None
    doubles: int | None
    home_runs: int | None
    ops: float | None
    era: float | None
    strikeouts: int | None
    wins: int | None
    whip: float | None
    qualified_hitter: bool
    qualified_pitcher: bool


class SeasonSnapshotResponse(BaseModel):
    season: int
    snapshot_label: str
    standings: list[TeamStandingResponse]
    players: list[LeaderboardPlayerResponse]


@router.get("/seasons", response_model=SeasonListResponse)
def get_seasons(session: Session = Depends(get_db)) -> SeasonListResponse:
    return SeasonListResponse(seasons=list_available_seasons(session))


@router.get("/seasons/{season}/snapshot", response_model=SeasonSnapshotResponse)
def get_season_snapshot(
    season: int,
    series_code: str | None = Query(default=None, pattern="^(preseason|regular|postseason)$"),
    session: Session = Depends(get_db),
) -> SeasonSnapshotResponse:
    snapshot = get_season_center_snapshot(session, season, series_code=series_code)
    if snapshot is None:
        raise HTTPException(status_code=404, detail="season not found")

    return SeasonSnapshotResponse(
        season=snapshot.season,
        snapshot_label=snapshot.snapshot_label,
        standings=[TeamStandingResponse(**asdict(item)) for item in snapshot.standings],
        players=[LeaderboardPlayerResponse(**asdict(item)) for item in snapshot.players],
    )
