from dataclasses import asdict
from typing import Any, cast

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.game_query_service import get_player_ingested_summary
from app.services.player_detail_service import get_player_season_detail
from app.schemas.player_detail import PlayerDetailLogResponse, PlayerDetailResponse
from pydantic import BaseModel

router = APIRouter(tags=["players"])


class BattingTotalsResponse(BaseModel):
    at_bats: int
    hits: int
    doubles: int
    triples: int
    home_runs: int
    walks: int
    hit_by_pitch: int
    sacrifice_flies: int


class PitchingTotalsResponse(BaseModel):
    innings_outs: int
    hits_allowed: int
    walks_allowed: int
    strikeouts: int


class PlayerSummaryResponse(BaseModel):
    player_key: str
    player_name: str
    scope: str
    games_count: int
    batting_totals: BattingTotalsResponse
    batting_metrics: dict[str, float | int | None]
    pitching_totals: PitchingTotalsResponse
    pitching_metrics: dict[str, float | None]


@router.get("/players/{player_key}/summary", response_model=PlayerSummaryResponse)
def get_player_summary(
    player_key: str,
    scope: str = Query(default="ingested"),
    session: Session = Depends(get_db),
) -> PlayerSummaryResponse:
    if scope != "ingested":
        raise HTTPException(status_code=400, detail="only scope=ingested is supported")

    summary = get_player_ingested_summary(session, player_key)
    if summary is None:
        raise HTTPException(status_code=404, detail="player not found")

    response_data = cast(dict[str, Any], summary)

    return PlayerSummaryResponse(
        player_key=str(summary["player_key"]),
        player_name=str(summary["player_name"]),
        scope="ingested",
        games_count=int(response_data["games_count"]),
        batting_totals=BattingTotalsResponse(**asdict(response_data["batting_totals"])),
        pitching_totals=PitchingTotalsResponse(**asdict(response_data["pitching_totals"])),
        batting_metrics=response_data["batting_metrics"],
        pitching_metrics=response_data["pitching_metrics"],
    )


@router.get("/players/{player_key}/season-detail", response_model=PlayerDetailResponse)
def get_player_detail(
    player_key: str,
    season: int,
    group: str = Query(pattern="^(hitters|pitchers)$"),
    series_code: str | None = Query(default=None, pattern="^(preseason|regular|postseason)$"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    session: Session = Depends(get_db),
) -> PlayerDetailResponse:
    detail = get_player_season_detail(
        session=session,
        player_key=player_key,
        season=season,
        series_code=series_code,
        group=group,
        page=page,
        page_size=page_size,
    )
    if detail is None:
        raise HTTPException(status_code=404, detail="player not found")

    return PlayerDetailResponse(
        player_key=str(detail["player_key"]),
        player_name=str(detail["player_name"]),
        team_code=str(detail["team_code"]),
        group=str(detail["group"]),
        season=int(detail["season"]),
        series_code=cast(str | None, detail["series_code"]),
        qualified=bool(detail["qualified"]),
        totals=cast(dict[str, int | str], detail["totals"]),
        metrics=cast(dict[str, float | int | None], detail["metrics"]),
        page=int(detail["page"]),
        page_size=int(detail["page_size"]),
        total_count=int(detail["total_count"]),
        total_pages=int(detail["total_pages"]),
        logs=[PlayerDetailLogResponse(**item) for item in cast(list[dict[str, object]], detail["logs"])],
    )
