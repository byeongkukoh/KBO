from pathlib import Path

from sqlalchemy import func, select

from app.db.session import get_session_factory
from app.ingest.orchestrators.ingest_game import ingest_single_game
from app.models import Game, PlayerGameBattingStat, PlayerGamePitchingStat, Team


def test_ingest_single_game_is_idempotent(sqlite_db_url: str) -> None:
    fixture_dir = Path(__file__).parent / "fixtures" / "kbo"
    session_factory = get_session_factory()

    with session_factory() as session:
        first = ingest_single_game(
            session=session,
            game_date="20260314",
            game_id="20260314WONC0",
            fixture_dir=fixture_dir,
            use_live=False,
        )
    assert first["status"] == "success"

    with session_factory() as session:
        second = ingest_single_game(
            session=session,
            game_date="20260314",
            game_id="20260314WONC0",
            fixture_dir=fixture_dir,
            use_live=False,
        )
    assert second["status"] == "success"

    with session_factory() as session:
        assert session.scalar(select(func.count(Game.id))) == 1
        assert session.scalar(select(func.count(Team.id))) == 2
        assert session.scalar(select(func.count(PlayerGameBattingStat.id))) == 6
        assert session.scalar(select(func.count(PlayerGamePitchingStat.id))) == 4
