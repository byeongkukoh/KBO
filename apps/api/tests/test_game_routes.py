from pathlib import Path

from app.db.session import get_session_factory
from app.ingest.orchestrators.ingest_game import ingest_single_game


def _seed_one_game() -> None:
    fixture_dir = Path(__file__).parent / "fixtures" / "kbo"
    session_factory = get_session_factory()
    with session_factory() as session:
        ingest_single_game(
            session=session,
            game_date="20260314",
            game_id="20260314WONC0",
            fixture_dir=fixture_dir,
            use_live=False,
        )


def test_get_game_detail_contract(client) -> None:
    _seed_one_game()

    response = client.get("/api/games/20260314WONC0")

    assert response.status_code == 200
    data = response.json()
    assert data["game_id"] == "20260314WONC0"
    assert data["away_team_code"] == "WO"
    assert data["home_team_code"] == "NC"
    assert len(data["innings"]) == 9
    assert len(data["batting_rows"]) == 6
    assert len(data["pitching_rows"]) == 4


def test_get_player_summary_ingested_scope(client) -> None:
    _seed_one_game()

    response = client.get("/api/players/wo-안치홍/summary", params={"scope": "ingested"})

    assert response.status_code == 200
    data = response.json()
    assert data["player_key"] == "wo-안치홍"
    assert data["batting_metrics"]["singles"] == 1
    assert data["batting_metrics"]["total_bases"] == 7
    assert data["batting_metrics"]["ops"] == 2.55


def test_get_player_summary_rejects_unsupported_scope(client) -> None:
    response = client.get("/api/players/wo-안치홍/summary", params={"scope": "career"})
    assert response.status_code == 400
