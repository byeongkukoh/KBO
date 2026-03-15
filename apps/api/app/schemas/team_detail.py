from pydantic import BaseModel


class TeamRecentGameResponse(BaseModel):
    game_id: str
    game_date: str
    series_code: str
    stadium: str
    result: str
    opponent_team_code: str
    team_score: int
    opponent_score: int


class TeamSeasonDetailResponse(BaseModel):
    season: int
    series_code: str | None
    team_code: str
    team_name: str
    wins: int
    losses: int
    draws: int
    win_pct: float | None
    runs_scored: int
    runs_allowed: int
    run_diff: int
    hits: int
    doubles: int
    stolen_bases: int
    batting_avg: float | None
    ops: float | None
    era: float | None
    whip: float | None
    ops_plus: float | None
    era_plus: float | None
    last_ten: str
    streak: str
    recent_games: list[TeamRecentGameResponse]
