from collections import defaultdict
from dataclasses import dataclass, field
from sqlalchemy import Select, select
from sqlalchemy.orm import Session, selectinload

from app.models import Game, PlayerGameBattingStat, PlayerGamePitchingStat, TeamGameStat
from app.services.derived_stats import BattingTotals, safe_ratio


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
    ops: float | None
    era: float | None
    strikeouts: int | None
    wins: int | None
    whip: float | None
    qualified_hitter: bool
    qualified_pitcher: bool


@dataclass(slots=True)
class SeasonCenterSnapshot:
    season: int
    snapshot_label: str
    standings: list[TeamStandingSnapshot]
    players: list[LeaderboardPlayerSnapshot]


@dataclass(slots=True)
class _TeamAccumulator:
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
    innings_outs: int = 0
    pitching_hits_allowed: int = 0
    pitching_walks_allowed: int = 0
    earned_runs: int = 0
    recent_results: list[str] = field(default_factory=list)


@dataclass(slots=True)
class _PlayerBattingAccumulator:
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
    walks: int = 0
    hit_by_pitch: int = 0
    sacrifice_flies: int = 0


@dataclass(slots=True)
class _PlayerPitchingAccumulator:
    player_id: str
    player_name: str
    team_code: str
    games: int = 0
    innings_outs: int = 0
    hits_allowed: int = 0
    walks_allowed: int = 0
    strikeouts: int = 0
    earned_runs: int = 0


def list_available_seasons(session: Session) -> list[int]:
    rows = session.execute(select(Game.season_id).distinct().order_by(Game.season_id.desc())).all()
    return [int(row[0]) for row in rows]


def get_season_center_snapshot(session: Session, season: int) -> SeasonCenterSnapshot | None:
    stmt: Select[tuple[Game]] = (
        select(Game)
        .where(Game.season_id == season)
        .options(
            selectinload(Game.away_team),
            selectinload(Game.home_team),
            selectinload(Game.team_game_stats).selectinload(TeamGameStat.team),
            selectinload(Game.player_batting_stats).selectinload(PlayerGameBattingStat.team),
            selectinload(Game.player_pitching_stats).selectinload(PlayerGamePitchingStat.team),
        )
        .order_by(Game.game_date.asc(), Game.kbo_game_id.asc())
    )
    games = list(session.execute(stmt).scalars())
    if not games:
        return None

    team_accumulators = _accumulate_teams(games)
    standings = _build_standings(team_accumulators)
    players = _build_player_snapshots(games, {item.team_code: item.games for item in standings})
    latest_date = max(game.game_date for game in games)

    return SeasonCenterSnapshot(
        season=season,
        snapshot_label=f"{latest_date.isoformat()} db snapshot",
        standings=standings,
        players=players,
    )


def _accumulate_teams(games: list[Game]) -> dict[str, _TeamAccumulator]:
    accumulators: dict[str, _TeamAccumulator] = {}

    for game in games:
        team_stats_by_id = {item.team_id: item for item in game.team_game_stats}
        batting_rows_by_team: dict[int, list[PlayerGameBattingStat]] = defaultdict(list)
        pitching_rows_by_team: dict[int, list[PlayerGamePitchingStat]] = defaultdict(list)

        for row in game.player_batting_stats:
            batting_rows_by_team[row.team_id].append(row)
        for row in game.player_pitching_stats:
            pitching_rows_by_team[row.team_id].append(row)

        for team, runs_for, runs_against in (
            (game.away_team, game.away_score, game.home_score),
            (game.home_team, game.home_score, game.away_score),
        ):
            team_stat = team_stats_by_id.get(team.id)
            if team.team_code not in accumulators:
                accumulators[team.team_code] = _TeamAccumulator(team_code=team.team_code, team_name=team.team_name)
            accumulator = accumulators[team.team_code]
            accumulator.games += 1
            accumulator.runs_scored += runs_for
            accumulator.runs_allowed += runs_against

            if runs_for > runs_against:
                accumulator.wins += 1
                accumulator.recent_results.append("W")
            elif runs_for < runs_against:
                accumulator.losses += 1
                accumulator.recent_results.append("L")
            else:
                accumulator.draws += 1
                accumulator.recent_results.append("D")

            if team_stat is not None:
                accumulator.hits += team_stat.hits

            for batting_row in batting_rows_by_team.get(team.id, []):
                accumulator.doubles += batting_row.doubles
                accumulator.at_bats += batting_row.at_bats
                accumulator.batting_hits += batting_row.hits
                accumulator.walks += batting_row.walks
                accumulator.hit_by_pitch += batting_row.hit_by_pitch
                accumulator.sacrifice_flies += batting_row.sacrifice_flies
                accumulator.triples += batting_row.triples
                accumulator.home_runs += batting_row.home_runs

            for pitching_row in pitching_rows_by_team.get(team.id, []):
                accumulator.innings_outs += pitching_row.innings_outs
                accumulator.pitching_hits_allowed += pitching_row.hits_allowed
                accumulator.pitching_walks_allowed += pitching_row.walks_allowed
                accumulator.earned_runs += pitching_row.earned_runs

    return accumulators


def _build_standings(accumulators: dict[str, _TeamAccumulator]) -> list[TeamStandingSnapshot]:
    snapshots: list[TeamStandingSnapshot] = []

    for accumulator in accumulators.values():
        batting_totals = BattingTotals(
            at_bats=accumulator.at_bats,
            hits=accumulator.batting_hits,
            doubles=accumulator.doubles,
            triples=accumulator.triples,
            home_runs=accumulator.home_runs,
            walks=accumulator.walks,
            hit_by_pitch=accumulator.hit_by_pitch,
            sacrifice_flies=accumulator.sacrifice_flies,
        )
        singles = max(
            batting_totals.hits - batting_totals.doubles - batting_totals.triples - batting_totals.home_runs,
            0,
        )
        total_bases = singles + batting_totals.doubles * 2 + batting_totals.triples * 3 + batting_totals.home_runs * 4
        win_pct = safe_ratio(accumulator.wins, accumulator.wins + accumulator.losses)
        obp = safe_ratio(
            batting_totals.hits + batting_totals.walks + batting_totals.hit_by_pitch,
            batting_totals.at_bats + batting_totals.walks + batting_totals.hit_by_pitch + batting_totals.sacrifice_flies,
        )
        slg = safe_ratio(total_bases, batting_totals.at_bats)
        ops = round(obp + slg, 3) if obp is not None and slg is not None else None
        innings = accumulator.innings_outs / 3
        era = safe_ratio(accumulator.earned_runs * 9, innings)
        whip = safe_ratio(accumulator.pitching_hits_allowed + accumulator.pitching_walks_allowed, innings)

        last_ten_slice = accumulator.recent_results[-10:]
        last_ten = f"{last_ten_slice.count('W')}-{last_ten_slice.count('L')}"
        streak = _format_streak(accumulator.recent_results)

        snapshots.append(
            TeamStandingSnapshot(
                rank=0,
                games=accumulator.games,
                team_code=accumulator.team_code,
                team_name=accumulator.team_name,
                wins=accumulator.wins,
                losses=accumulator.losses,
                draws=accumulator.draws,
                win_pct=win_pct,
                games_back=0.0,
                runs_scored=accumulator.runs_scored,
                runs_allowed=accumulator.runs_allowed,
                run_diff=accumulator.runs_scored - accumulator.runs_allowed,
                hits=accumulator.hits,
                doubles=accumulator.doubles,
                batting_avg=safe_ratio(batting_totals.hits, batting_totals.at_bats),
                obp=obp,
                slg=slg,
                ops=ops,
                home_runs=accumulator.home_runs,
                stolen_bases=None,
                era=era,
                whip=whip,
                last_ten=last_ten,
                streak=streak,
            )
        )

    snapshots.sort(
        key=lambda item: (
            -(item.win_pct if item.win_pct is not None else -1.0),
            -item.run_diff,
            -item.runs_scored,
        )
    )
    leader_win_pct = snapshots[0].win_pct or 0.0
    leader_games = snapshots[0].games

    for index, snapshot in enumerate(snapshots, start=1):
        games_back = ((leader_win_pct * leader_games) - snapshot.wins + snapshot.losses - (snapshot.games - leader_games) * leader_win_pct) / 2 if index > 1 else 0.0
        snapshot.rank = index
        snapshot.games_back = round(games_back, 1)

    return snapshots


def _build_player_snapshots(games: list[Game], team_games_by_code: dict[str, int]) -> list[LeaderboardPlayerSnapshot]:
    batting: dict[str, _PlayerBattingAccumulator] = {}
    pitching: dict[str, _PlayerPitchingAccumulator] = {}

    for game in games:
        for row in game.player_batting_stats:
            team_code = row.team.team_code
            accumulator = batting.setdefault(
                row.player_key,
                _PlayerBattingAccumulator(player_id=row.player_key, player_name=row.player_name, team_code=team_code),
            )
            accumulator.games += 1
            accumulator.plate_appearances += row.plate_appearances
            accumulator.at_bats += row.at_bats
            accumulator.hits += row.hits
            accumulator.doubles += row.doubles
            accumulator.triples += row.triples
            accumulator.home_runs += row.home_runs
            accumulator.walks += row.walks
            accumulator.hit_by_pitch += row.hit_by_pitch
            accumulator.sacrifice_flies += row.sacrifice_flies

        for row in game.player_pitching_stats:
            team_code = row.team.team_code
            accumulator = pitching.setdefault(
                row.player_key,
                _PlayerPitchingAccumulator(player_id=row.player_key, player_name=row.player_name, team_code=team_code),
            )
            accumulator.games += 1
            accumulator.innings_outs += row.innings_outs
            accumulator.hits_allowed += row.hits_allowed
            accumulator.walks_allowed += row.walks_allowed
            accumulator.strikeouts += row.strikeouts
            accumulator.earned_runs += row.earned_runs

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
        innings = round(accumulator.innings_outs / 3, 1)
        outs = accumulator.innings_outs
        team_games = team_games_by_code.get(accumulator.team_code, 0)
        qualified_pitcher = outs >= team_games * 3 if team_games > 0 else False

        snapshots.append(
            LeaderboardPlayerSnapshot(
                player_id=accumulator.player_id,
                player_name=accumulator.player_name,
                team_code=accumulator.team_code,
                games=accumulator.games,
                plate_appearances=None,
                innings=innings,
                batting_avg=None,
                hits=None,
                doubles=None,
                home_runs=None,
                ops=None,
                era=safe_ratio(accumulator.earned_runs * 27, outs),
                strikeouts=accumulator.strikeouts,
                wins=None,
                whip=safe_ratio(accumulator.hits_allowed + accumulator.walks_allowed, outs / 3 if outs > 0 else 0),
                qualified_hitter=False,
                qualified_pitcher=qualified_pitcher,
            )
        )

    snapshots.sort(key=lambda item: (item.team_code, item.player_name))
    return snapshots


def _format_streak(results: list[str]) -> str:
    if not results:
        return "-"

    last = results[-1]
    if last == "D":
        return "D1"

    count = 0
    for result in reversed(results):
        if result != last:
            break
        count += 1
    return f"{last}{count}"
