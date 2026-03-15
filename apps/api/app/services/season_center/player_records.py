from math import ceil

from app.models import LeagueSeasonBattingContext, LeagueSeasonPitchingContext
from app.services.derived_stats import BattingTotals, PitchingTotals, derive_batting_metrics, derive_fip_metric, derive_pitching_metrics, derive_woba_metrics, safe_ratio
from app.services.season_center.types import LeaderboardPlayerSnapshot, PlayerBattingAccumulator, PlayerPitchingAccumulator, PlayerRecordRow, PlayerRecordsPage

HITTER_SORT_KEYS = {"avg", "hits", "doubles", "homeRuns", "stolenBases", "ops", "iso", "babip", "bbRate", "kRate"}
PITCHER_SORT_KEYS = {"era", "strikeouts", "wins", "whip", "kPer9", "bbPer9", "kbb"}


def build_player_snapshots(
    batting: dict[str, PlayerBattingAccumulator],
    pitching: dict[str, PlayerPitchingAccumulator],
    team_games_by_code: dict[str, int],
    batting_context: LeagueSeasonBattingContext | None = None,
    pitching_context: LeagueSeasonPitchingContext | None = None,
    constants: dict[str, float] | None = None,
) -> list[LeaderboardPlayerSnapshot]:
    snapshots: list[LeaderboardPlayerSnapshot] = []

    for accumulator in batting.values():
        batting_totals = BattingTotals(
            at_bats=accumulator.at_bats,
            hits=accumulator.hits,
            doubles=accumulator.doubles,
            triples=accumulator.triples,
            home_runs=accumulator.home_runs,
            strikeouts=accumulator.strikeouts,
            walks=accumulator.walks,
            intentional_walks=0,
            hit_by_pitch=accumulator.hit_by_pitch,
            sacrifice_flies=accumulator.sacrifice_flies,
        )
        batting_metrics = derive_batting_metrics(batting_totals)
        advanced_batting = _derive_advanced_batting(batting_totals, batting_context, constants)
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
                batting_avg=cast_float(batting_metrics["avg"]),
                hits=accumulator.hits,
                doubles=accumulator.doubles,
                home_runs=accumulator.home_runs,
                stolen_bases=accumulator.stolen_bases,
                ops=cast_float(batting_metrics["ops"]),
                iso=cast_float(batting_metrics["iso"]),
                babip=cast_float(batting_metrics["babip"]),
                bb_rate=cast_float(batting_metrics["bb_rate"]),
                k_rate=cast_float(batting_metrics["k_rate"]),
                woba=cast_float(advanced_batting["woba"]),
                wrc=cast_float(advanced_batting["wrc"]),
                wrc_plus=cast_float(advanced_batting["wrc_plus"]),
                era=None,
                strikeouts=None,
                wins=None,
                whip=None,
                k_per_9=None,
                bb_per_9=None,
                kbb=None,
                fip=None,
                qualified_hitter=qualified_hitter,
                qualified_pitcher=False,
            )
        )

    for accumulator in pitching.values():
        team_games = team_games_by_code.get(accumulator.team_code, 0)
        qualified_pitcher = accumulator.innings_outs >= team_games * 3 if team_games > 0 else False
        pitching_metrics = derive_pitching_metrics(
            PitchingTotals(
                innings_outs=accumulator.innings_outs,
                hits_allowed=accumulator.hits_allowed,
                walks_allowed=accumulator.walks_allowed,
                hit_by_pitch_allowed=0,
                strikeouts=accumulator.strikeouts,
                home_runs_allowed=0,
            )
        )
        advanced_pitching = _derive_advanced_pitching(accumulator, pitching_context, constants)
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
                iso=None,
                babip=None,
                bb_rate=None,
                k_rate=None,
                woba=None,
                wrc=None,
                wrc_plus=None,
                era=safe_ratio(accumulator.earned_runs * 27, accumulator.innings_outs),
                strikeouts=accumulator.strikeouts,
                wins=accumulator.wins,
                whip=cast_float(pitching_metrics["whip"]),
                k_per_9=cast_float(pitching_metrics["k_per_9"]),
                bb_per_9=cast_float(pitching_metrics["bb_per_9"]),
                kbb=cast_float(pitching_metrics["kbb"]),
                fip=cast_float(advanced_pitching["fip"]),
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
                iso=player.iso,
                babip=player.babip,
                bb_rate=player.bb_rate,
                k_rate=player.k_rate,
                woba=player.woba,
                wrc=player.wrc,
                wrc_plus=player.wrc_plus,
                era=player.era,
                strikeouts=player.strikeouts,
                wins=player.wins,
                whip=player.whip,
                k_per_9=player.k_per_9,
                bb_per_9=player.bb_per_9,
                kbb=player.kbb,
                fip=player.fip,
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
        "iso": player.iso,
        "babip": player.babip,
        "bbRate": player.bb_rate,
        "kRate": player.k_rate,
        "woba": player.woba,
        "wrc": player.wrc,
        "wrcPlus": player.wrc_plus,
        "era": player.era,
        "strikeouts": player.strikeouts,
        "wins": player.wins,
        "whip": player.whip,
        "kPer9": player.k_per_9,
        "bbPer9": player.bb_per_9,
        "kbb": player.kbb,
        "fip": player.fip,
    }
    value = mapping.get(sort_key)
    return float(value) if value is not None else -1.0


def cast_float(value: float | int | None) -> float | None:
    if value is None:
        return None
    return float(value)


def _derive_advanced_batting(totals: BattingTotals, batting_context: LeagueSeasonBattingContext | None, constants: dict[str, float] | None) -> dict[str, float | None]:
    if batting_context is None or constants is None or batting_context.plate_appearances == 0:
        return {"woba": None, "wrc": None, "wrc_plus": None}
    return derive_woba_metrics(
        totals,
        unintentional_walk_weight=constants.get("WOBA_U_BB_WEIGHT", 0.69),
        hit_by_pitch_weight=constants.get("WOBA_HBP_WEIGHT", 0.72),
        single_weight=constants.get("WOBA_1B_WEIGHT", 0.89),
        double_weight=constants.get("WOBA_2B_WEIGHT", 1.27),
        triple_weight=constants.get("WOBA_3B_WEIGHT", 1.62),
        home_run_weight=constants.get("WOBA_HR_WEIGHT", 2.10),
        woba_scale=constants.get("WOBA_SCALE", 1.25),
        league_woba=constants.get("LEAGUE_WOBA", batting_context.ops or 0.0),
        league_runs_per_pa=constants.get("LEAGUE_R_PER_PA", batting_context.runs_scored / batting_context.plate_appearances),
    )


def _derive_advanced_pitching(accumulator: PlayerPitchingAccumulator, pitching_context: LeagueSeasonPitchingContext | None, constants: dict[str, float] | None) -> dict[str, float | None]:
    if constants is None:
        return {"fip": None}
    totals = PitchingTotals(
        innings_outs=accumulator.innings_outs,
        hits_allowed=accumulator.hits_allowed,
        walks_allowed=accumulator.walks_allowed,
        hit_by_pitch_allowed=0,
        strikeouts=accumulator.strikeouts,
        home_runs_allowed=0,
    )
    return {"fip": derive_fip_metric(totals, fip_constant=constants.get("FIP_CONSTANT", 0.0))}


def _innings_outs_from_float(value: float | None) -> int | None:
    if value is None:
        return None
    whole = int(value)
    remainder = int(round((value - whole) * 10))
    return whole * 3 + remainder
