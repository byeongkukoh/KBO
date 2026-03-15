from app.db.session import get_session_factory
from app.services.league_context_service import refresh_league_context
from tests.test_season_routes import _seed_season_center_data


def test_get_team_season_detail(client) -> None:
    _seed_season_center_data()
    session_factory = get_session_factory()
    with session_factory() as session:
        refresh_league_context(session=session, season=2026, series_code="regular")
        session.commit()

    response = client.get("/api/teams/SS/season-detail", params={"season": 2026, "series_code": "regular"})

    assert response.status_code == 200
    data = response.json()
    assert data["team_code"] == "SS"
    assert data["wins"] == 2
    assert data["recent_games"][0]["game_id"] == "20260403SSLG0"
    assert data["ops_plus"] is not None
    assert data["era_plus"] is not None


def test_get_games_list(client) -> None:
    _seed_season_center_data()

    response = client.get("/api/games", params={"season": 2026, "series_code": "regular", "page": 1, "page_size": 2})

    assert response.status_code == 200
    data = response.json()
    assert data["total_count"] == 3
    assert len(data["items"]) == 2
    assert data["items"][0]["game_id"] == "20260403SSLG0"


def test_refresh_league_context_persists_rows(sqlite_db_url: str) -> None:
    _seed_season_center_data()
    session_factory = get_session_factory()
    with session_factory() as session:
        refresh_league_context(session=session, season=2026, series_code="regular")
        session.commit()
        from app.models import AdvancedMetricConstant, LeagueSeasonBattingContext, LeagueSeasonPitchingContext

        batting = session.query(LeagueSeasonBattingContext).filter_by(season_id=2026, series_code="regular").one()
        pitching = session.query(LeagueSeasonPitchingContext).filter_by(season_id=2026, series_code="regular").one()
        constants = session.query(AdvancedMetricConstant).filter_by(season_id=2026, series_code="regular").all()

    assert batting.ops is not None
    assert pitching.era is not None
    assert {item.metric_code for item in constants} == {"OPS_PLUS_BASELINE", "ERA_PLUS_BASELINE"}
