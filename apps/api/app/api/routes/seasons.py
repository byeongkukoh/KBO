from dataclasses import asdict

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.season_center import LeaderboardPlayerResponse, PlayerRecordRowResponse, PlayerRecordsPageResponse, SeasonListResponse, SeasonSnapshotResponse, TeamStandingResponse
from app.services.season_center_query_service import get_player_records_page, get_season_center_snapshot, list_available_seasons

router = APIRouter(tags=["seasons"])


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


@router.get("/seasons/{season}/player-records", response_model=PlayerRecordsPageResponse)
def get_season_player_records(
    season: int,
    group: str = Query(pattern="^(hitters|pitchers)$"),
    sort_key: str = Query(default="avg"),
    qualified_only: bool = Query(default=True),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
    series_code: str | None = Query(default=None, pattern="^(preseason|regular|postseason)$"),
    session: Session = Depends(get_db),
) -> PlayerRecordsPageResponse:
    result = get_player_records_page(
        session=session,
        season=season,
        series_code=series_code,
        group=group,
        sort_key=sort_key,
        qualified_only=qualified_only,
        page=page,
        page_size=page_size,
    )
    if result is None:
        raise HTTPException(status_code=404, detail="season not found")

    return PlayerRecordsPageResponse(
        season=result.season,
        series_code=result.series_code,
        group=result.group,
        sort_key=result.sort_key,
        qualified_only=result.qualified_only,
        page=result.page,
        page_size=result.page_size,
        total_count=result.total_count,
        total_pages=result.total_pages,
        snapshot_label=result.snapshot_label,
        items=[PlayerRecordRowResponse(**asdict(item)) for item in result.items],
    )
