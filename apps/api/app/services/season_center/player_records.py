from math import ceil

from app.services.derived_stats import safe_ratio
from app.services.season_center.types import LeaderboardPlayerSnapshot, PlayerBattingAccumulator, PlayerPitchingAccumulator, PlayerRecordRow, PlayerRecordsPage

HITTER_SORT_KEYS = {"avg", "hits", "doubles", "homeRuns", "stolenBases", "ops"}
PITCHER_SORT_KEYS = {"era", "strikeouts", "wins", "whip"}


def build_player_snapshots(
    batting: dict[str, PlayerBattingAccumulator],
    pitching: dict[str, PlayerPitchingAccumulator],
    team_games_by_code: dict[str, int],
) -> list[LeaderboardPlayerSnapshot]:
    snapshots: list[LeaderboardPlayerSnapshot] = []

    for accumulator in batting.values():
        singles = max(accumulator.hits - accumulator.doubles - accumulator.triples - accumulator.home_runs, 0)
        total_bases = singles + accumulator.doubles * 2 + accumulator.triples * 3 + accumulator.home_runs * 4
        obp = safe_ratio(
            accumulator.hits + accumulator.walks + accumulator.hit_by_pitch,
            accumulator.at_bats + accumulator.walks + accumulator.hit_by_pitch + accumulator.sacrifice_flies,
        )
        slg = safe_ratio(total_bases, accumulator.at_bats)
        ops = round(obp + slg, 3) if obp is not None and slg is not None else None
        team_games = team_games_by_code.get(accumulator.team_code, 0)
        qualified_hitter = accumulator.plate_appearances >= team_games * 3.1 if team_games > 0 else False
        snapshots.append(
            LeaderboardPlayerSnapshot(
                player_id=accumulator.player_id,
                player_name=accumulator.player_name,
                team_code=accumulator.team_code,
                games=accumulator.games,
                plate_appearances=accumulator.plate_appearances,
                innings=None,
                batting_avg=safe_ratio(accumulator.hits, accumulator.at_bats),
                hits=accumulator.hits,
                doubles=accumulator.doubles,
                home_runs=accumulator.home_runs,
                stolen_bases=accumulator.stolen_bases,
                ops=ops,
                era=None,
                strikeouts=None,
                wins=None,
                whip=None,
                qualified_hitter=qualified_hitter,
                qualified_pitcher=False,
            )
        )

    for accumulator in pitching.values():
        team_games = team_games_by_code.get(accumulator.team_code, 0)
        qualified_pitcher = accumulator.innings_outs >= team_games * 3 if team_games > 0 else False
        snapshots.append(
            LeaderboardPlayerSnapshot(
                player_id=accumulator.player_id,
                player_name=accumulator.player_name,
                team_code=accumulator.team_code,
                games=accumulator.games,
                plate_appearances=None,
                innings=round(accumulator.innings_outs / 3, 1),
                batting_avg=None,
                hits=None,
                doubles=None,
                home_runs=None,
                stolen_bases=None,
                ops=None,
                era=safe_ratio(accumulator.earned_runs * 27, accumulator.innings_outs),
                strikeouts=accumulator.strikeouts,
                wins=accumulator.wins,
                whip=safe_ratio(accumulator.hits_allowed + accumulator.walks_allowed, accumulator.innings_outs / 3 if accumulator.innings_outs > 0 else 0),
                qualified_hitter=False,
                qualified_pitcher=qualified_pitcher,
            )
        )

    snapshots.sort(key=lambda item: (item.team_code, item.player_name))
    return snapshots


def build_player_records_page(
    season: int,
    series_code: str | None,
    snapshot_label: str,
    players: list[LeaderboardPlayerSnapshot],
    group: str,
    sort_key: str,
    qualified_only: bool,
    page: int,
    page_size: int,
) -> PlayerRecordsPage:
    filtered = _filter_players(players, group=group, qualified_only=qualified_only)
    ranked = _sort_and_rank(filtered, group=group, sort_key=sort_key)
    total_count = len(ranked)
    total_pages = max(1, ceil(total_count / page_size)) if total_count else 1
    current_page = min(max(page, 1), total_pages)
    start = (current_page - 1) * page_size
    end = start + page_size

    return PlayerRecordsPage(
        season=season,
        series_code=series_code,
        group=group,
        sort_key=sort_key,
        qualified_only=qualified_only,
        page=current_page,
        page_size=page_size,
        total_count=total_count,
        total_pages=total_pages,
        snapshot_label=snapshot_label,
        items=ranked[start:end],
    )


def format_innings_display(outs: int) -> str:
    whole = outs // 3
    remainder = outs % 3
    return f"{whole}.{remainder}"


def _filter_players(players: list[LeaderboardPlayerSnapshot], group: str, qualified_only: bool) -> list[LeaderboardPlayerSnapshot]:
    rows: list[LeaderboardPlayerSnapshot] = []
    for player in players:
        if group == "hitters":
            if player.batting_avg is None:
                continue
            if qualified_only and not player.qualified_hitter:
                continue
            rows.append(player)
            continue
        if player.era is None:
            continue
        if qualified_only and not player.qualified_pitcher:
            continue
        rows.append(player)
    return rows


def _sort_and_rank(players: list[LeaderboardPlayerSnapshot], group: str, sort_key: str) -> list[PlayerRecordRow]:
    if group == "hitters" and sort_key not in HITTER_SORT_KEYS:
        sort_key = "avg"
    if group == "pitchers" and sort_key not in PITCHER_SORT_KEYS:
        sort_key = "era"

    descending = sort_key not in {"era", "whip"}

    def key_func(player: LeaderboardPlayerSnapshot) -> tuple[float, str]:
        value = _player_sort_value(player, sort_key)
        return (value, player.player_name)

    ordered = sorted(players, key=key_func, reverse=descending)
    rows: list[PlayerRecordRow] = []
    for index, player in enumerate(ordered, start=1):
        innings_outs = None if player.era is None else _innings_outs_from_float(player.innings)
        rows.append(
            PlayerRecordRow(
                rank=index,
                player_type="hitter" if group == "hitters" else "pitcher",
                player_id=player.player_id,
                player_name=player.player_name,
                team_code=player.team_code,
                games=player.games,
                plate_appearances=player.plate_appearances,
                innings=player.innings,
                innings_display=None if innings_outs is None else format_innings_display(innings_outs),
                innings_outs=innings_outs,
                batting_avg=player.batting_avg,
                hits=player.hits,
                doubles=player.doubles,
                home_runs=player.home_runs,
                stolen_bases=player.stolen_bases,
                ops=player.ops,
                era=player.era,
                strikeouts=player.strikeouts,
                wins=player.wins,
                whip=player.whip,
                qualified_hitter=player.qualified_hitter,
                qualified_pitcher=player.qualified_pitcher,
            )
        )
    return rows


def _player_sort_value(player: LeaderboardPlayerSnapshot, sort_key: str) -> float:
    mapping = {
        "avg": player.batting_avg,
        "hits": player.hits,
        "doubles": player.doubles,
        "homeRuns": player.home_runs,
        "stolenBases": player.stolen_bases,
        "ops": player.ops,
        "era": player.era,
        "strikeouts": player.strikeouts,
        "wins": player.wins,
        "whip": player.whip,
    }
    value = mapping.get(sort_key)
    return float(value) if value is not None else -1.0


def _innings_outs_from_float(value: float | None) -> int | None:
    if value is None:
        return None
    whole = int(value)
    remainder = int(round((value - whole) * 10))
    return whole * 3 + remainder
