import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.ingest.http_client import FixtureClient, KBOClient
from app.ingest.parsers.review_parser import PlayerBattingParsed, PlayerPitchingParsed, parse_boxscore_payload
from app.ingest.parsers.scoreboard_parser import parse_scoreboard_payload
from app.models import (
    DataSyncItem,
    DataSyncRun,
    Game,
    GameSourcePage,
    InningScore,
    PlayerGameBattingStat,
    PlayerGamePitchingStat,
    Team,
    TeamGameStat,
)


def ingest_single_game(
    session: Session,
    game_date: str,
    game_id: str,
    fixture_dir: Path | None = None,
    use_live: bool = False,
) -> dict[str, Any]:
    run = DataSyncRun(game_date=game_date, game_id=game_id, status="running")
    session.add(run)
    session.commit()
    session.refresh(run)

    client: FixtureClient | KBOClient = KBOClient() if use_live else FixtureClient(fixture_dir or Path("tests/fixtures/kbo"))
    try:
        game_list = client.fetch_game_list(game_date)
        game_meta = _pick_game_meta(game_list, game_id)
        scoreboard_payload = client.fetch_scoreboard(
            le_id=int(game_meta["LE_ID"]),
            sr_id=int(game_meta["SR_ID"]),
            season_id=int(game_meta["SEASON_ID"]),
            game_id=game_id,
        )
        boxscore_payload = client.fetch_boxscore(
            le_id=int(game_meta["LE_ID"]),
            sr_id=int(game_meta["SR_ID"]),
            season_id=int(game_meta["SEASON_ID"]),
            game_id=game_id,
        )

        session.add_all(
            [
                DataSyncItem(run_id=run.id, source_type="game_list", external_key=game_date, status="success"),
                DataSyncItem(run_id=run.id, source_type="scoreboard", external_key=game_id, status="success"),
                DataSyncItem(run_id=run.id, source_type="boxscore", external_key=game_id, status="success"),
            ]
        )

        scoreboard = parse_scoreboard_payload(scoreboard_payload, status_code=str(game_meta["GAME_STATE_SC"]))
        review = parse_boxscore_payload(boxscore_payload, scoreboard.away_team.team_code, scoreboard.home_team.team_code)

        away_team = _upsert_team(session, scoreboard.away_team.team_code, scoreboard.away_team.team_name)
        home_team = _upsert_team(session, scoreboard.home_team.team_code, scoreboard.home_team.team_name)

        game = session.execute(select(Game).where(Game.kbo_game_id == game_id)).scalar_one_or_none()
        if game is None:
            game = Game(
                kbo_game_id=scoreboard.game_id,
                game_date=scoreboard.game_date,
                season_id=scoreboard.season_id,
                le_id=scoreboard.le_id,
                sr_id=scoreboard.sr_id,
                series_code=_series_code_from_meta(sr_id=scoreboard.sr_id, game_sc_name=str(game_meta.get("GAME_SC_NM", ""))),
                series_name=str(game_meta.get("GAME_SC_NM", "")) or _series_name_from_sr_id(scoreboard.sr_id),
                status_code=scoreboard.status_code,
                stadium=scoreboard.stadium,
                away_team_id=away_team.id,
                home_team_id=home_team.id,
                away_score=scoreboard.away_team.runs,
                home_score=scoreboard.home_team.runs,
            )
            session.add(game)
            session.flush()
        else:
            game.game_date = scoreboard.game_date
            game.season_id = scoreboard.season_id
            game.le_id = scoreboard.le_id
            game.sr_id = scoreboard.sr_id
            game.series_code = _series_code_from_meta(sr_id=scoreboard.sr_id, game_sc_name=str(game_meta.get("GAME_SC_NM", "")))
            game.series_name = str(game_meta.get("GAME_SC_NM", "")) or _series_name_from_sr_id(scoreboard.sr_id)
            game.status_code = scoreboard.status_code
            game.stadium = scoreboard.stadium
            game.away_team_id = away_team.id
            game.home_team_id = home_team.id
            game.away_score = scoreboard.away_team.runs
            game.home_score = scoreboard.home_team.runs

        session.execute(delete(InningScore).where(InningScore.game_id == game.id))
        session.execute(delete(TeamGameStat).where(TeamGameStat.game_id == game.id))
        session.execute(delete(PlayerGameBattingStat).where(PlayerGameBattingStat.game_id == game.id))
        session.execute(delete(PlayerGamePitchingStat).where(PlayerGamePitchingStat.game_id == game.id))
        session.execute(delete(GameSourcePage).where(GameSourcePage.game_id == game.id))

        session.add_all(
            [
                InningScore(game_id=game.id, inning_no=item.inning_no, away_runs=item.away_runs, home_runs=item.home_runs)
                for item in scoreboard.innings
            ]
        )
        session.add_all(
            [
                TeamGameStat(
                    game_id=game.id,
                    team_id=away_team.id,
                    runs=scoreboard.away_team.runs,
                    hits=scoreboard.away_team.hits,
                    errors=scoreboard.away_team.errors,
                    walks=scoreboard.away_team.walks,
                ),
                TeamGameStat(
                    game_id=game.id,
                    team_id=home_team.id,
                    runs=scoreboard.home_team.runs,
                    hits=scoreboard.home_team.hits,
                    errors=scoreboard.home_team.errors,
                    walks=scoreboard.home_team.walks,
                ),
            ]
        )

        team_ids = {scoreboard.away_team.team_code: away_team.id, scoreboard.home_team.team_code: home_team.id}
        for row in _merge_batting_rows(review.batting_rows):
            session.add(
                PlayerGameBattingStat(
                    game_id=game.id,
                    team_id=team_ids[row.team_code],
                    player_key=row.player_key,
                    player_name=row.player_name,
                    batting_order=row.batting_order,
                    position_code=row.position_code,
                    plate_appearances=row.plate_appearances,
                    at_bats=row.at_bats,
                    runs=row.runs,
                    hits=row.hits,
                    doubles=row.doubles,
                    triples=row.triples,
                    home_runs=row.home_runs,
                    stolen_bases=row.stolen_bases,
                    runs_batted_in=row.runs_batted_in,
                    walks=row.walks,
                    intentional_walks=row.intentional_walks,
                    hit_by_pitch=row.hit_by_pitch,
                    sacrifice_flies=row.sacrifice_flies,
                    strikeouts=row.strikeouts,
                )
            )

        for row in _merge_pitching_rows(review.pitching_rows):
            session.add(
                PlayerGamePitchingStat(
                    game_id=game.id,
                    team_id=team_ids[row.team_code],
                    player_key=row.player_key,
                    player_name=row.player_name,
                    innings_outs=row.innings_outs,
                    batters_faced=row.batters_faced,
                    pitches_thrown=row.pitches_thrown,
                    at_bats=row.at_bats,
                    hits_allowed=row.hits_allowed,
                    home_runs_allowed=row.home_runs_allowed,
                    walks_allowed=row.walks_allowed,
                    hit_by_pitch_allowed=row.hit_by_pitch_allowed,
                    strikeouts=row.strikeouts,
                    runs_allowed=row.runs_allowed,
                    earned_runs=row.earned_runs,
                    decision_code=row.decision_code,
                )
            )

        sources = {
            "game_list": {
                "url": f"/ws/Main.asmx/GetKboGameList?date={game_date}",
                "payload": game_list,
            },
            "scoreboard": {
                "url": f"/ws/Schedule.asmx/GetScoreBoardScroll?gameId={game_id}",
                "payload": scoreboard_payload,
            },
            "boxscore": {
                "url": f"/ws/Schedule.asmx/GetBoxScoreScroll?gameId={game_id}",
                "payload": boxscore_payload,
            },
        }
        for source_type, source_data in sources.items():
            payload_text = json.dumps(source_data["payload"], ensure_ascii=False, sort_keys=True)
            session.add(
                GameSourcePage(
                    game_id=game.id,
                    source_type=source_type,
                    source_url=source_data["url"],
                    parser_version="v1",
                    checksum=hashlib.sha256(payload_text.encode("utf-8")).hexdigest(),
                )
            )

        run.status = "success"
        run.finished_at = datetime.now(tz=timezone.utc)
        session.commit()
        return {"run_id": run.id, "game_id": game_id, "status": "success"}
    except Exception as exc:
        session.rollback()
        run.status = "failed"
        run.error_message = str(exc)
        run.finished_at = datetime.now(tz=timezone.utc)
        session.commit()
        raise


def _pick_game_meta(game_list_payload: dict[str, Any], game_id: str) -> dict[str, Any]:
    for item in game_list_payload.get("game", []):
        if item.get("G_ID") == game_id:
            return item
    raise ValueError(f"game_id not found in game list: {game_id}")


def _upsert_team(session: Session, team_code: str, team_name: str) -> Team:
    team = session.execute(select(Team).where(Team.team_code == team_code)).scalar_one_or_none()
    if team is None:
        team = Team(team_code=team_code, team_name=team_name)
        session.add(team)
        session.flush()
    else:
        team.team_name = team_name
    return team


def _series_code_from_meta(sr_id: int, game_sc_name: str) -> str:
    if sr_id == 1:
        return "preseason"
    if sr_id == 0:
        return "regular"
    if sr_id in {3, 4, 5, 7}:
        return "postseason"
    if "시범" in game_sc_name:
        return "preseason"
    if "정규" in game_sc_name:
        return "regular"
    if any(token in game_sc_name for token in ["WC", "준PO", "PO", "KS", "포스트"]):
        return "postseason"
    return "other"


def _series_name_from_sr_id(sr_id: int) -> str:
    return {
        1: "시범경기",
        0: "정규경기",
        3: "준플레이오프",
        4: "와일드카드",
        5: "플레이오프",
        7: "한국시리즈",
    }.get(sr_id, "기타")


def _merge_batting_rows(rows: list[PlayerBattingParsed]) -> list[PlayerBattingParsed]:
    merged: dict[tuple[str, str], PlayerBattingParsed] = {}
    for row in rows:
        key = (row.team_code, row.player_key)
        existing = merged.get(key)
        if existing is None:
            merged[key] = row
            continue
        merged[key] = PlayerBattingParsed(
            team_code=row.team_code,
            player_key=row.player_key,
            player_name=row.player_name,
            batting_order=min(existing.batting_order, row.batting_order),
            position_code=row.position_code,
            plate_appearances=existing.plate_appearances + row.plate_appearances,
            at_bats=existing.at_bats + row.at_bats,
            runs=existing.runs + row.runs,
            hits=existing.hits + row.hits,
            doubles=existing.doubles + row.doubles,
            triples=existing.triples + row.triples,
            home_runs=existing.home_runs + row.home_runs,
            stolen_bases=existing.stolen_bases + row.stolen_bases,
            runs_batted_in=existing.runs_batted_in + row.runs_batted_in,
            walks=existing.walks + row.walks,
            intentional_walks=existing.intentional_walks + row.intentional_walks,
            hit_by_pitch=existing.hit_by_pitch + row.hit_by_pitch,
            sacrifice_flies=existing.sacrifice_flies + row.sacrifice_flies,
            strikeouts=existing.strikeouts + row.strikeouts,
        )
    return list(merged.values())


def _merge_pitching_rows(rows: list[PlayerPitchingParsed]) -> list[PlayerPitchingParsed]:
    merged: dict[tuple[str, str], PlayerPitchingParsed] = {}
    for row in rows:
        key = (row.team_code, row.player_key)
        existing = merged.get(key)
        if existing is None:
            merged[key] = row
            continue
        merged[key] = PlayerPitchingParsed(
            team_code=row.team_code,
            player_key=row.player_key,
            player_name=row.player_name,
            innings_outs=existing.innings_outs + row.innings_outs,
            batters_faced=existing.batters_faced + row.batters_faced,
            pitches_thrown=existing.pitches_thrown + row.pitches_thrown,
            at_bats=existing.at_bats + row.at_bats,
            hits_allowed=existing.hits_allowed + row.hits_allowed,
            home_runs_allowed=existing.home_runs_allowed + row.home_runs_allowed,
            walks_allowed=existing.walks_allowed + row.walks_allowed,
            hit_by_pitch_allowed=existing.hit_by_pitch_allowed + row.hit_by_pitch_allowed,
            strikeouts=existing.strikeouts + row.strikeouts,
            runs_allowed=existing.runs_allowed + row.runs_allowed,
            earned_runs=existing.earned_runs + row.earned_runs,
            decision_code=existing.decision_code or row.decision_code,
        )
    return list(merged.values())
