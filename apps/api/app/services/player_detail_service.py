from math import ceil

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models import Game, PlayerGameBattingStat, PlayerGamePitchingStat
from app.services.derived_stats import BattingTotals, PitchingTotals, derive_batting_metrics, derive_pitching_metrics
from app.services.season_center.player_records import format_innings_display


def get_player_season_detail(
    session: Session,
    player_key: str,
    season: int,
    series_code: str | None,
    group: str,
    page: int,
    page_size: int,
) -> dict[str, object] | None:
    if group == "hitters":
        return _get_hitter_detail(session, player_key, season, series_code, page, page_size)
    return _get_pitcher_detail(session, player_key, season, series_code, page, page_size)


def _build_hitter_season_rows(session: Session, player_key: str) -> list[dict[str, int | float | str | bool | None]]:
    stmt: Select[tuple[PlayerGameBattingStat]] = (
        select(PlayerGameBattingStat)
        .join(Game, PlayerGameBattingStat.game_id == Game.id)
        .where(PlayerGameBattingStat.player_key == player_key)
        .options(selectinload(PlayerGameBattingStat.team))
    )
    rows = list(session.execute(stmt).scalars())
    grouped: dict[tuple[int, str], list[PlayerGameBattingStat]] = {}
    for row in rows:
        key = (row.game.season_id, row.team.team_code)
        grouped.setdefault(key, []).append(row)
    season_rows: list[dict[str, int | float | str | bool | None]] = []
    for (season_id, team_code), items in sorted(grouped.items(), reverse=True):
        totals = BattingTotals(
            at_bats=sum(item.at_bats for item in items),
            hits=sum(item.hits for item in items),
            doubles=sum(item.doubles for item in items),
            triples=sum(item.triples for item in items),
            home_runs=sum(item.home_runs for item in items),
            walks=sum(item.walks for item in items),
            hit_by_pitch=sum(item.hit_by_pitch for item in items),
            sacrifice_flies=sum(item.sacrifice_flies for item in items),
        )
        season_rows.append(
            {
                "season": season_id,
                "team_code": team_code,
                "games": len(items),
                "qualified": sum(item.plate_appearances for item in items) >= _get_team_games_count(session, items[0].team_id, season_id, None) * 3.1,
                "plate_appearances": sum(item.plate_appearances for item in items),
                "hits": totals.hits,
                "home_runs": totals.home_runs,
                "stolen_bases": sum(item.stolen_bases for item in items),
                "batting_avg": derive_batting_metrics(totals)["avg"],
                "ops": derive_batting_metrics(totals)["ops"],
            }
        )
    return season_rows


def _build_pitcher_season_rows(session: Session, player_key: str) -> list[dict[str, int | float | str | bool | None]]:
    stmt: Select[tuple[PlayerGamePitchingStat]] = (
        select(PlayerGamePitchingStat)
        .join(Game, PlayerGamePitchingStat.game_id == Game.id)
        .where(PlayerGamePitchingStat.player_key == player_key)
        .options(selectinload(PlayerGamePitchingStat.team))
    )
    rows = list(session.execute(stmt).scalars())
    grouped: dict[tuple[int, str], list[PlayerGamePitchingStat]] = {}
    for row in rows:
        key = (row.game.season_id, row.team.team_code)
        grouped.setdefault(key, []).append(row)
    season_rows: list[dict[str, int | float | str | bool | None]] = []
    for (season_id, team_code), items in sorted(grouped.items(), reverse=True):
        totals = PitchingTotals(
            innings_outs=sum(item.innings_outs for item in items),
            hits_allowed=sum(item.hits_allowed for item in items),
            walks_allowed=sum(item.walks_allowed for item in items),
            strikeouts=sum(item.strikeouts for item in items),
        )
        metrics = derive_pitching_metrics(totals)
        season_rows.append(
            {
                "season": season_id,
                "team_code": team_code,
                "games": len(items),
                "qualified": totals.innings_outs >= _get_team_games_count(session, items[0].team_id, season_id, None) * 3,
                "innings_outs": totals.innings_outs,
                "innings_display": format_innings_display(totals.innings_outs),
                "wins": sum(1 for item in items if item.decision_code == "승"),
                "strikeouts": totals.strikeouts,
                "era": round(sum(item.earned_runs for item in items) * 27 / totals.innings_outs, 3) if totals.innings_outs > 0 else None,
                "whip": metrics["whip"],
            }
        )
    return season_rows


def _get_hitter_detail(session: Session, player_key: str, season: int, series_code: str | None, page: int, page_size: int) -> dict[str, object] | None:
    stmt: Select[tuple[PlayerGameBattingStat]] = (
        select(PlayerGameBattingStat)
        .join(Game, PlayerGameBattingStat.game_id == Game.id)
        .where(PlayerGameBattingStat.player_key == player_key, Game.season_id == season)
        .options(selectinload(PlayerGameBattingStat.game), selectinload(PlayerGameBattingStat.team))
        .order_by(Game.game_date.desc(), Game.kbo_game_id.desc())
    )
    if series_code is not None:
        stmt = stmt.where(Game.series_code == series_code)
    rows = list(session.execute(stmt).scalars())
    if not rows:
        return None

    latest = rows[0]
    team_games = _get_team_games_count(session, team_id=latest.team_id, season=season, series_code=series_code)
    totals = BattingTotals(
        at_bats=sum(item.at_bats for item in rows),
        hits=sum(item.hits for item in rows),
        doubles=sum(item.doubles for item in rows),
        triples=sum(item.triples for item in rows),
        home_runs=sum(item.home_runs for item in rows),
        walks=sum(item.walks for item in rows),
        hit_by_pitch=sum(item.hit_by_pitch for item in rows),
        sacrifice_flies=sum(item.sacrifice_flies for item in rows),
    )
    metrics = derive_batting_metrics(totals)
    total_count = len(rows)
    total_pages = max(1, ceil(total_count / page_size))
    current_page = min(max(page, 1), total_pages)
    page_rows = rows[(current_page - 1) * page_size : current_page * page_size]

    return {
        "player_key": player_key,
        "player_name": latest.player_name,
        "team_code": latest.team.team_code,
        "group": "hitters",
        "season": season,
        "series_code": series_code,
        "qualified": sum(item.plate_appearances for item in rows) >= team_games * 3.1 if team_games > 0 else False,
        "totals": {
            "games": total_count,
            "plate_appearances": sum(item.plate_appearances for item in rows),
            "at_bats": totals.at_bats,
            "hits": totals.hits,
            "doubles": totals.doubles,
            "triples": totals.triples,
            "home_runs": totals.home_runs,
            "stolen_bases": sum(item.stolen_bases for item in rows),
            "walks": totals.walks,
            "runs_batted_in": sum(item.runs_batted_in for item in rows),
        },
        "metrics": metrics,
        "page": current_page,
        "page_size": page_size,
        "total_count": total_count,
        "total_pages": total_pages,
        "seasons": _build_hitter_season_rows(session, player_key),
        "logs": [
            {
                "game_id": item.game.kbo_game_id,
                "game_date": item.game.game_date.isoformat(),
                "series_code": item.game.series_code,
                "stadium": item.game.stadium,
                "position_code": item.position_code,
                "plate_appearances": item.plate_appearances,
                "at_bats": item.at_bats,
                "hits": item.hits,
                "doubles": item.doubles,
                "triples": item.triples,
                "home_runs": item.home_runs,
                "stolen_bases": item.stolen_bases,
                "walks": item.walks,
                "runs_batted_in": item.runs_batted_in,
                "strikeouts": item.strikeouts,
                "result": _game_result_for_team(item.game, item.team.team_code),
                "opponent_team_code": _opponent_team_code(item.game, item.team.team_code),
            }
            for item in page_rows
        ],
    }


def _get_pitcher_detail(session: Session, player_key: str, season: int, series_code: str | None, page: int, page_size: int) -> dict[str, object] | None:
    stmt: Select[tuple[PlayerGamePitchingStat]] = (
        select(PlayerGamePitchingStat)
        .join(Game, PlayerGamePitchingStat.game_id == Game.id)
        .where(PlayerGamePitchingStat.player_key == player_key, Game.season_id == season)
        .options(selectinload(PlayerGamePitchingStat.game), selectinload(PlayerGamePitchingStat.team))
        .order_by(Game.game_date.desc(), Game.kbo_game_id.desc())
    )
    if series_code is not None:
        stmt = stmt.where(Game.series_code == series_code)
    rows = list(session.execute(stmt).scalars())
    if not rows:
        return None

    latest = rows[0]
    team_games = _get_team_games_count(session, team_id=latest.team_id, season=season, series_code=series_code)
    totals = PitchingTotals(
        innings_outs=sum(item.innings_outs for item in rows),
        hits_allowed=sum(item.hits_allowed for item in rows),
        walks_allowed=sum(item.walks_allowed for item in rows),
        strikeouts=sum(item.strikeouts for item in rows),
    )
    metrics = derive_pitching_metrics(totals)
    total_count = len(rows)
    total_pages = max(1, ceil(total_count / page_size))
    current_page = min(max(page, 1), total_pages)
    page_rows = rows[(current_page - 1) * page_size : current_page * page_size]

    return {
        "player_key": player_key,
        "player_name": latest.player_name,
        "team_code": latest.team.team_code,
        "group": "pitchers",
        "season": season,
        "series_code": series_code,
        "qualified": totals.innings_outs >= team_games * 3 if team_games > 0 else False,
        "totals": {
            "games": total_count,
            "innings_outs": totals.innings_outs,
            "innings_display": format_innings_display(totals.innings_outs),
            "hits_allowed": totals.hits_allowed,
            "walks_allowed": totals.walks_allowed,
            "strikeouts": totals.strikeouts,
            "wins": sum(1 for item in rows if item.decision_code == "승"),
            "earned_runs": sum(item.earned_runs for item in rows),
        },
        "metrics": metrics,
        "page": current_page,
        "page_size": page_size,
        "total_count": total_count,
        "total_pages": total_pages,
        "seasons": _build_pitcher_season_rows(session, player_key),
        "logs": [
            {
                "game_id": item.game.kbo_game_id,
                "game_date": item.game.game_date.isoformat(),
                "series_code": item.game.series_code,
                "stadium": item.game.stadium,
                "innings_outs": item.innings_outs,
                "innings_display": format_innings_display(item.innings_outs),
                "hits_allowed": item.hits_allowed,
                "walks_allowed": item.walks_allowed,
                "strikeouts": item.strikeouts,
                "earned_runs": item.earned_runs,
                "decision_code": item.decision_code,
                "result": _game_result_for_team(item.game, item.team.team_code),
                "opponent_team_code": _opponent_team_code(item.game, item.team.team_code),
            }
            for item in page_rows
        ],
    }


def _get_team_games_count(session: Session, team_id: int, season: int, series_code: str | None) -> int:
    stmt = select(func.count(Game.id)).where(
        Game.season_id == season,
        or_(Game.away_team_id == team_id, Game.home_team_id == team_id),
    )
    if series_code is not None:
        stmt = stmt.where(Game.series_code == series_code)
    return int(session.execute(stmt).scalar_one())


def _game_result_for_team(game: Game, team_code: str) -> str:
    is_home = game.home_team.team_code == team_code
    team_score = game.home_score if is_home else game.away_score
    opponent_score = game.away_score if is_home else game.home_score
    if team_score > opponent_score:
        return "W"
    if team_score < opponent_score:
        return "L"
    return "D"


def _opponent_team_code(game: Game, team_code: str) -> str:
    return game.away_team.team_code if game.home_team.team_code == team_code else game.home_team.team_code
