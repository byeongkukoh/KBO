from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
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
    innings: list[InningScoreResponse]
    team_stats: list[TeamStatResponse]
    batting_rows: list[BattingRowResponse]
    pitching_rows: list[PitchingRowResponse]


@router.get("/games/{game_id}", response_model=GameDetailResponse)
def get_game(game_id: str, session: Session = Depends(get_db)) -> GameDetailResponse:
    game = get_game_detail(session, game_id)
    if game is None:
        raise HTTPException(status_code=404, detail="game not found")

    return GameDetailResponse(
        game_id=game.kbo_game_id,
        game_date=game.game_date.isoformat(),
        status_code=game.status_code,
        stadium=game.stadium,
        away_team_code=game.away_team.team_code,
        home_team_code=game.home_team.team_code,
        away_score=game.away_score,
        home_score=game.home_score,
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
