from dataclasses import dataclass, field


@dataclass(slots=True)
class TeamStandingSnapshot:
    rank: int
    games: int
    team_code: str
    team_name: str
    wins: int
    losses: int
    draws: int
    win_pct: float | None
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


@dataclass(slots=True)
class LeaderboardPlayerSnapshot:
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


@dataclass(slots=True)
class PlayerRecordRow:
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


@dataclass(slots=True)
class PlayerRecordsPage:
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
    items: list[PlayerRecordRow]


@dataclass(slots=True)
class SeasonCenterSnapshot:
    season: int
    snapshot_label: str
    standings: list[TeamStandingSnapshot]
    players: list[LeaderboardPlayerSnapshot]


@dataclass(slots=True)
class TeamAccumulator:
    team_code: str
    team_name: str
    games: int = 0
    wins: int = 0
    losses: int = 0
    draws: int = 0
    runs_scored: int = 0
    runs_allowed: int = 0
    hits: int = 0
    doubles: int = 0
    at_bats: int = 0
    batting_hits: int = 0
    walks: int = 0
    hit_by_pitch: int = 0
    sacrifice_flies: int = 0
    triples: int = 0
    home_runs: int = 0
    stolen_bases: int = 0
    innings_outs: int = 0
    pitching_hits_allowed: int = 0
    pitching_walks_allowed: int = 0
    earned_runs: int = 0
    recent_results: list[str] = field(default_factory=list)


@dataclass(slots=True)
class PlayerBattingAccumulator:
    player_id: str
    player_name: str
    team_code: str
    games: int = 0
    plate_appearances: int = 0
    at_bats: int = 0
    hits: int = 0
    doubles: int = 0
    triples: int = 0
    home_runs: int = 0
    stolen_bases: int = 0
    walks: int = 0
    hit_by_pitch: int = 0
    sacrifice_flies: int = 0


@dataclass(slots=True)
class PlayerPitchingAccumulator:
    player_id: str
    player_name: str
    team_code: str
    games: int = 0
    innings_outs: int = 0
    hits_allowed: int = 0
    walks_allowed: int = 0
    strikeouts: int = 0
    earned_runs: int = 0
    wins: int = 0
