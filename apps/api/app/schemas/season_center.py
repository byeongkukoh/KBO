from pydantic import BaseModel


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
    stolen_bases: int | None
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


class PlayerRecordRowResponse(BaseModel):
    rank: int
    player_type: str
    player_id: str
    player_name: str
    team_code: str
    games: int
    plate_appearances: int | None
    innings: float | None
    innings_display: str | None
    innings_outs: int | None
    batting_avg: float | None
    hits: int | None
    doubles: int | None
    home_runs: int | None
    stolen_bases: int | None
    ops: float | None
    era: float | None
    strikeouts: int | None
    wins: int | None
    whip: float | None
    qualified_hitter: bool
    qualified_pitcher: bool


class PlayerRecordsPageResponse(BaseModel):
    season: int
    series_code: str | None
    group: str
    sort_key: str
    qualified_only: bool
    page: int
    page_size: int
    total_count: int
    total_pages: int
    snapshot_label: str
    items: list[PlayerRecordRowResponse]
