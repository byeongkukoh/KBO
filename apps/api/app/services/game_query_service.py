from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session, selectinload

from app.models import Game, PlayerGameBattingStat, PlayerGamePitchingStat, TeamGameStat
from app.services.derived_stats import BattingTotals, PitchingTotals, derive_batting_metrics, derive_pitching_metrics


def get_game_detail(session: Session, game_id: str) -> Game | None:
    stmt: Select[tuple[Game]] = (
        select(Game)
        .where(Game.kbo_game_id == game_id)
        .options(
            selectinload(Game.inning_scores),
            selectinload(Game.team_game_stats).selectinload(TeamGameStat.team),
            selectinload(Game.player_batting_stats).selectinload(PlayerGameBattingStat.team),
            selectinload(Game.player_pitching_stats).selectinload(PlayerGamePitchingStat.team),
            selectinload(Game.away_team),
            selectinload(Game.home_team),
        )
    )
    return session.execute(stmt).scalar_one_or_none()


def get_player_ingested_summary(session: Session, player_key: str) -> dict[str, object] | None:
    batting_row = session.execute(
        select(
            func.coalesce(func.sum(PlayerGameBattingStat.at_bats), 0),
            func.coalesce(func.sum(PlayerGameBattingStat.hits), 0),
            func.coalesce(func.sum(PlayerGameBattingStat.doubles), 0),
            func.coalesce(func.sum(PlayerGameBattingStat.triples), 0),
            func.coalesce(func.sum(PlayerGameBattingStat.home_runs), 0),
            func.coalesce(func.sum(PlayerGameBattingStat.walks), 0),
            func.coalesce(func.sum(PlayerGameBattingStat.hit_by_pitch), 0),
            func.coalesce(func.sum(PlayerGameBattingStat.sacrifice_flies), 0),
            func.max(PlayerGameBattingStat.player_name),
            func.count(PlayerGameBattingStat.id),
        ).where(PlayerGameBattingStat.player_key == player_key)
    ).one()

    pitching_row = session.execute(
        select(
            func.coalesce(func.sum(PlayerGamePitchingStat.innings_outs), 0),
            func.coalesce(func.sum(PlayerGamePitchingStat.hits_allowed), 0),
            func.coalesce(func.sum(PlayerGamePitchingStat.walks_allowed), 0),
            func.coalesce(func.sum(PlayerGamePitchingStat.strikeouts), 0),
            func.max(PlayerGamePitchingStat.player_name),
            func.count(PlayerGamePitchingStat.id),
        ).where(PlayerGamePitchingStat.player_key == player_key)
    ).one()

    batting_count = int(batting_row[9])
    pitching_count = int(pitching_row[5])
    if batting_count == 0 and pitching_count == 0:
        return None

    player_name = batting_row[8] or pitching_row[4] or player_key

    batting_totals = BattingTotals(
        at_bats=int(batting_row[0]),
        hits=int(batting_row[1]),
        doubles=int(batting_row[2]),
        triples=int(batting_row[3]),
        home_runs=int(batting_row[4]),
        walks=int(batting_row[5]),
        hit_by_pitch=int(batting_row[6]),
        sacrifice_flies=int(batting_row[7]),
    )

    pitching_totals = PitchingTotals(
        innings_outs=int(pitching_row[0]),
        hits_allowed=int(pitching_row[1]),
        walks_allowed=int(pitching_row[2]),
        strikeouts=int(pitching_row[3]),
    )

    return {
        "player_key": player_key,
        "player_name": player_name,
        "scope": "ingested",
        "batting_totals": batting_totals,
        "pitching_totals": pitching_totals,
        "batting_metrics": derive_batting_metrics(batting_totals),
        "pitching_metrics": derive_pitching_metrics(pitching_totals),
        "games_count": max(batting_count, pitching_count),
    }
