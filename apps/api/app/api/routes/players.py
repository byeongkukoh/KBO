from dataclasses import asdict
from typing import Any, cast

from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.game_query_service import get_player_ingested_summary

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
