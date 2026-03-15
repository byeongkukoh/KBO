from pydantic import BaseModel

from app.schemas.freshness import FreshnessResponse


class PlayerDetailLogResponse(BaseModel):
    game_id: str
    game_date: str
    series_code: str
    stadium: str
    result: str
    opponent_team_code: str
    position_code: str | None = None
    plate_appearances: int | None = None
    at_bats: int | None = None
    hits: int | None = None
    doubles: int | None = None
    triples: int | None = None
    home_runs: int | None = None
    stolen_bases: int | None = None
    walks: int | None = None
    runs_batted_in: int | None = None
    strikeouts: int | None = None
    innings_outs: int | None = None
    innings_display: str | None = None
    hits_allowed: int | None = None
    walks_allowed: int | None = None
    earned_runs: int | None = None
    decision_code: str | None = None


class PlayerMonthlySplitResponse(BaseModel):
    month: int
    month_label: str
    games: int
    plate_appearances: int | None = None
    innings_outs: int | None = None
    innings_display: str | None = None
    batting_avg: float | None = None
    hits: int | None = None
    home_runs: int | None = None
    stolen_bases: int | None = None
    ops: float | None = None
    iso: float | None = None
    babip: float | None = None
    bb_rate: float | None = None
    k_rate: float | None = None
    woba: float | None = None
    wrc: float | None = None
    wrc_plus: float | None = None
    era: float | None = None
    whip: float | None = None
    k_per_9: float | None = None
    bb_per_9: float | None = None
    kbb: float | None = None
    fip: float | None = None


class PlayerDetailResponse(BaseModel):
    player_key: str
    player_name: str
    team_code: str
    group: str
    season: int
    series_code: str | None
    qualified: bool
    totals: dict[str, int | str]
    metrics: dict[str, float | int | None]
    page: int
    page_size: int
    total_count: int
    total_pages: int
    freshness: FreshnessResponse
    seasons: list[dict[str, int | float | str | bool | None]]
    monthly_splits: list[PlayerMonthlySplitResponse]
    logs: list[PlayerDetailLogResponse]


class PlayerComparisonItemResponse(BaseModel):
    player_key: str
    player_name: str
    team_code: str
    qualified: bool
    metrics: dict[str, float | int | None]
    monthly_splits: list[PlayerMonthlySplitResponse]


class PlayerComparisonResponse(BaseModel):
    season: int
    series_code: str | None
    group: str
    freshness: FreshnessResponse
    players: list[PlayerComparisonItemResponse]
