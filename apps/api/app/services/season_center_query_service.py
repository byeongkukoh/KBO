from collections import defaultdict

from sqlalchemy import Select, select
from sqlalchemy.orm import Session, selectinload

from app.models import AdvancedMetricConstant, Game, LeagueSeasonBattingContext, LeagueSeasonPitchingContext, PlayerGameBattingStat, PlayerGamePitchingStat, TeamGameStat
from app.services.season_center import (
    LeaderboardPlayerSnapshot,
    PlayerBattingAccumulator,
    PlayerPitchingAccumulator,
    PlayerRecordsPage,
    SeasonCenterSnapshot,
    TeamAccumulator,
    build_player_records_page,
    build_team_standings,
)


def list_available_seasons(session: Session) -> list[int]:
    rows = session.execute(select(Game.season_id).distinct().order_by(Game.season_id.desc())).all()
    return [int(row[0]) for row in rows]


def get_season_center_snapshot(session: Session, season: int, series_code: str | None = None) -> SeasonCenterSnapshot | None:
    games = _load_games(session, season=season, series_code=series_code)
    if not games:
        return None

    team_accumulators, batting, pitching = _accumulate_games(games)
    standings = build_team_standings(team_accumulators)
    batting_context, pitching_context, constants = _load_metric_context(session, season=season, series_code=series_code)
    players = _build_snapshot_players(
        batting,
        pitching,
        {item.team_code: item.games for item in standings},
        batting_context=batting_context,
        pitching_context=pitching_context,
        constants=constants,
    )
    latest_date = max(game.game_date for game in games)

    return SeasonCenterSnapshot(
        season=season,
        snapshot_label=f"{latest_date.isoformat()} db snapshot" if series_code is None else f"{latest_date.isoformat()} {series_code} db snapshot",
        standings=standings,
        players=players,
    )


def get_player_records_page(
    session: Session,
    season: int,
    series_code: str | None,
    group: str,
    sort_key: str,
    qualified_only: bool,
    page: int,
    page_size: int,
) -> PlayerRecordsPage | None:
    snapshot = get_season_center_snapshot(session, season=season, series_code=series_code)
    if snapshot is None:
        return None
    return build_player_records_page(
        season=snapshot.season,
        series_code=series_code,
        snapshot_label=snapshot.snapshot_label,
        players=snapshot.players,
        group=group,
        sort_key=sort_key,
        qualified_only=qualified_only,
        page=page,
        page_size=page_size,
    )


def _load_games(session: Session, season: int, series_code: str | None) -> list[Game]:
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
    if series_code is not None:
        stmt = stmt.where(Game.series_code == series_code)
    return list(session.execute(stmt).scalars())


def _accumulate_games(
    games: list[Game],
) -> tuple[dict[str, TeamAccumulator], dict[str, PlayerBattingAccumulator], dict[str, PlayerPitchingAccumulator]]:
    team_accumulators: dict[str, TeamAccumulator] = {}
    batting: dict[str, PlayerBattingAccumulator] = {}
    pitching: dict[str, PlayerPitchingAccumulator] = {}

    for game in games:
        team_stats_by_id = {item.team_id: item for item in game.team_game_stats}
        batting_rows_by_team: dict[int, list[PlayerGameBattingStat]] = defaultdict(list)
        pitching_rows_by_team: dict[int, list[PlayerGamePitchingStat]] = defaultdict(list)

        for row in game.player_batting_stats:
            batting_rows_by_team[row.team_id].append(row)
            accumulator = batting.setdefault(
                row.player_key,
                PlayerBattingAccumulator(player_id=row.player_key, player_name=row.player_name, team_code=row.team.team_code),
            )
            accumulator.games += 1
            accumulator.plate_appearances += row.plate_appearances
            accumulator.at_bats += row.at_bats
            accumulator.hits += row.hits
            accumulator.doubles += row.doubles
            accumulator.triples += row.triples
            accumulator.home_runs += row.home_runs
            accumulator.stolen_bases += row.stolen_bases
            accumulator.strikeouts += row.strikeouts
            accumulator.walks += row.walks
            accumulator.hit_by_pitch += row.hit_by_pitch
            accumulator.sacrifice_flies += row.sacrifice_flies

        for row in game.player_pitching_stats:
            pitching_rows_by_team[row.team_id].append(row)
            accumulator = pitching.setdefault(
                row.player_key,
                PlayerPitchingAccumulator(player_id=row.player_key, player_name=row.player_name, team_code=row.team.team_code),
            )
            accumulator.games += 1
            accumulator.innings_outs += row.innings_outs
            accumulator.hits_allowed += row.hits_allowed
            accumulator.walks_allowed += row.walks_allowed
            accumulator.strikeouts += row.strikeouts
            accumulator.earned_runs += row.earned_runs
            if row.decision_code == "승":
                accumulator.wins += 1

        for team, runs_for, runs_against in (
            (game.away_team, game.away_score, game.home_score),
            (game.home_team, game.home_score, game.away_score),
        ):
            team_stat = team_stats_by_id.get(team.id)
            accumulator = team_accumulators.setdefault(team.team_code, TeamAccumulator(team_code=team.team_code, team_name=team.team_name))
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
                accumulator.stolen_bases += batting_row.stolen_bases

            for pitching_row in pitching_rows_by_team.get(team.id, []):
                accumulator.innings_outs += pitching_row.innings_outs
                accumulator.pitching_hits_allowed += pitching_row.hits_allowed
                accumulator.pitching_walks_allowed += pitching_row.walks_allowed
                accumulator.earned_runs += pitching_row.earned_runs

    return team_accumulators, batting, pitching


def _build_snapshot_players(
    batting: dict[str, PlayerBattingAccumulator],
    pitching: dict[str, PlayerPitchingAccumulator],
    team_games_by_code: dict[str, int],
    batting_context: LeagueSeasonBattingContext | None,
    pitching_context: LeagueSeasonPitchingContext | None,
    constants: dict[str, float],
) -> list[LeaderboardPlayerSnapshot]:
    from app.services.season_center.player_records import build_player_snapshots

    return build_player_snapshots(batting, pitching, team_games_by_code, batting_context=batting_context, pitching_context=pitching_context, constants=constants)


def _load_metric_context(session: Session, season: int, series_code: str | None) -> tuple[LeagueSeasonBattingContext | None, LeagueSeasonPitchingContext | None, dict[str, float]]:
    resolved_series = series_code or "regular"
    batting_context = session.execute(select(LeagueSeasonBattingContext).where(LeagueSeasonBattingContext.season_id == season, LeagueSeasonBattingContext.series_code == resolved_series)).scalar_one_or_none()
    pitching_context = session.execute(select(LeagueSeasonPitchingContext).where(LeagueSeasonPitchingContext.season_id == season, LeagueSeasonPitchingContext.series_code == resolved_series)).scalar_one_or_none()
    constants_rows = session.execute(select(AdvancedMetricConstant).where(AdvancedMetricConstant.season_id == season, AdvancedMetricConstant.series_code == resolved_series)).scalars().all()
    constants = {row.metric_code: row.metric_value for row in constants_rows}
    return batting_context, pitching_context, constants
