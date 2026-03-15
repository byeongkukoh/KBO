from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Any, cast

from app.db.session import get_db
from app.schemas.freshness import FreshnessResponse
from app.schemas.game_browse import GameListItemResponse, GameListResponse
from app.services.freshness_service import get_scope_freshness
from app.services.game_browse_service import list_games
from app.services.game_query_service import get_game_detail

router = APIRouter(tags=["games"])


class InningScoreResponse(BaseModel):
    inning_no: int
    away_runs: int
    home_runs: int


class TeamStatResponse(BaseModel):
    team_code: str
    team_name: str
    runs: int
    hits: int
    errors: int
    walks: int


class BattingRowResponse(BaseModel):
    team_code: str
    player_key: str
    player_name: str
    at_bats: int
    hits: int
    doubles: int
    triples: int
    home_runs: int
    walks: int
    hit_by_pitch: int
    sacrifice_flies: int


class PitchingRowResponse(BaseModel):
    team_code: str
    player_key: str
    player_name: str
    innings_outs: int
    hits_allowed: int
    walks_allowed: int
    strikeouts: int


class GameDetailResponse(BaseModel):
    game_id: str
    game_date: str
    status_code: str
    stadium: str
    away_team_code: str
    home_team_code: str
    away_score: int
    home_score: int
    freshness: FreshnessResponse
    innings: list[InningScoreResponse]
    team_stats: list[TeamStatResponse]
    batting_rows: list[BattingRowResponse]
    pitching_rows: list[PitchingRowResponse]


@router.get("/games", response_model=GameListResponse)
def get_games(
    season: int,
    series_code: str | None = Query(default=None, pattern="^(preseason|regular|postseason)$"),
    team_code: str | None = None,
    game_date: str | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    session: Session = Depends(get_db),
) -> GameListResponse:
    payload = list_games(session, season=season, series_code=series_code, team_code=team_code, game_date=game_date, page=page, page_size=page_size)
    payload_data = cast(dict[str, Any], payload)
    freshness = get_scope_freshness(session, season=season, series_code=series_code)
    return GameListResponse(
        season=int(payload_data["season"]),
        series_code=cast(str | None, payload_data["series_code"]),
        team_code=cast(str | None, payload_data["team_code"]),
        game_date=cast(str | None, payload_data["game_date"]),
        page=int(payload_data["page"]),
        page_size=int(payload_data["page_size"]),
        total_count=int(payload_data["total_count"]),
        total_pages=int(payload_data["total_pages"]),
        freshness=FreshnessResponse(**freshness),
        items=[GameListItemResponse(**cast(dict[str, Any], item)) for item in cast(list[dict[str, Any]], payload_data["items"])],
    )


@router.get("/games/{game_id}", response_model=GameDetailResponse)
def get_game(game_id: str, session: Session = Depends(get_db)) -> GameDetailResponse:
    game = get_game_detail(session, game_id)
    if game is None:
        raise HTTPException(status_code=404, detail="game not found")
    freshness = get_scope_freshness(session, season=game.season_id, series_code=game.series_code)

    return GameDetailResponse(
        game_id=game.kbo_game_id,
        game_date=game.game_date.isoformat(),
        status_code=game.status_code,
        stadium=game.stadium,
        away_team_code=game.away_team.team_code,
        home_team_code=game.home_team.team_code,
        away_score=game.away_score,
        home_score=game.home_score,
        freshness=FreshnessResponse(**freshness),
        innings=[
            InningScoreResponse(inning_no=i.inning_no, away_runs=i.away_runs, home_runs=i.home_runs)
            for i in sorted(game.inning_scores, key=lambda x: x.inning_no)
        ],
        team_stats=[
            TeamStatResponse(
                team_code=item.team.team_code,
                team_name=item.team.team_name,
                runs=item.runs,
                hits=item.hits,
                errors=item.errors,
                walks=item.walks,
            )
            for item in game.team_game_stats
        ],
        batting_rows=[
            BattingRowResponse(
                team_code=item.team.team_code,
                player_key=item.player_key,
                player_name=item.player_name,
                at_bats=item.at_bats,
                hits=item.hits,
                doubles=item.doubles,
                triples=item.triples,
                home_runs=item.home_runs,
                walks=item.walks,
                hit_by_pitch=item.hit_by_pitch,
                sacrifice_flies=item.sacrifice_flies,
            )
            for item in game.player_batting_stats
        ],
        pitching_rows=[
            PitchingRowResponse(
                team_code=item.team.team_code,
                player_key=item.player_key,
                player_name=item.player_name,
                innings_outs=item.innings_outs,
                hits_allowed=item.hits_allowed,
                walks_allowed=item.walks_allowed,
                strikeouts=item.strikeouts,
            )
            for item in game.player_pitching_stats
        ],
    )
