from pathlib import Path

import pytest
from sqlalchemy import func, select

from app.db.session import get_session_factory
from app.ingest.orchestrators.ingest_game import ingest_single_game, _merge_batting_rows, _merge_pitching_rows
from app.ingest.orchestrators import ingest_season as ingest_season_module
from app.ingest.orchestrators.ingest_season import ingest_season
from app.ingest.parsers.review_parser import PlayerBattingParsed, PlayerPitchingParsed
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


def test_merge_duplicate_batting_and_pitching_rows() -> None:
    batting_rows = [
        PlayerBattingParsed("WO", "wo-어준서", "어준서", 8, "SS", 2, 2, 1, 1, 0, 0, 0, 1, 0, 1, 0, 0, 1),
        PlayerBattingParsed("WO", "wo-어준서", "어준서", 9, "PH", 1, 1, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0),
    ]
    pitching_rows = [
        PlayerPitchingParsed("KT", "kt-박영현", "박영현", 2, 5, 18, 4, 1, 0, 0, 1, 0, 0, "승"),
        PlayerPitchingParsed("KT", "kt-박영현", "박영현", 1, 2, 9, 1, 0, 0, 1, 0, 0, 0, None),
    ]

    merged_batting = _merge_batting_rows(batting_rows)
    merged_pitching = _merge_pitching_rows(pitching_rows)

    assert len(merged_batting) == 1
    assert merged_batting[0].plate_appearances == 3
    assert merged_batting[0].at_bats == 3
    assert merged_batting[0].hits == 2
    assert merged_batting[0].doubles == 1
    assert merged_batting[0].walks == 1
    assert merged_batting[0].stolen_bases == 1

    assert len(merged_pitching) == 1
    assert merged_pitching[0].innings_outs == 3
    assert merged_pitching[0].batters_faced == 7
    assert merged_pitching[0].walks_allowed == 1
    assert merged_pitching[0].strikeouts == 1
    assert merged_pitching[0].decision_code == "승"


def test_ingest_season_filters_by_series_and_completed_state(monkeypatch: pytest.MonkeyPatch, sqlite_db_url: str) -> None:
    called: list[tuple[str, str]] = []

    class DummyFixtureClient:
        def __init__(self, fixture_dir: Path) -> None:
            self.fixture_dir = fixture_dir

        def fetch_game_list(self, game_date: str) -> dict[str, object]:
            if game_date == "20250308":
                return {
                    "game": [
                        {"G_ID": "20250308HTLT0", "LE_ID": 1, "SR_ID": 1, "SEASON_ID": 2025, "GAME_STATE_SC": "3"},
                        {"G_ID": "20250308ETCN0", "LE_ID": 1, "SR_ID": 9, "SEASON_ID": 2025, "GAME_STATE_SC": "3"},
                        {"G_ID": "20250308RAIN0", "LE_ID": 1, "SR_ID": 1, "SEASON_ID": 2025, "GAME_STATE_SC": "4"},
                    ]
                }
            return {"game": []}

    def fake_ingest_single_game(*, session, game_date: str, game_id: str, fixture_dir: Path | None, use_live: bool) -> dict[str, str]:
        called.append((game_date, game_id))
        return {"status": "success", "game_id": game_id}

    monkeypatch.setattr(ingest_season_module, "FixtureClient", DummyFixtureClient)
    monkeypatch.setattr(ingest_season_module, "ingest_single_game", fake_ingest_single_game)

    session_factory = get_session_factory()
    with session_factory() as session:
        summary = ingest_season(
            session=session,
            season=2025,
            series_groups=["preseason"],
            fixture_dir=Path("unused"),
            use_live=False,
            start_date=__import__("datetime").date(2025, 3, 8),
            end_date=__import__("datetime").date(2025, 3, 8),
        )

    assert called == [("20250308", "20250308HTLT0")]
    assert summary.matched_games == 1
    assert summary.ingested_games == 1
    assert summary.failed_games == 0
