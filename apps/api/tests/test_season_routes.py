from datetime import date

from app.db.session import get_session_factory
from app.models import Game, PlayerGameBattingStat, PlayerGamePitchingStat, Team, TeamGameStat


def _get_or_create_team(session, team_code: str, team_name: str) -> Team:
    team = session.query(Team).filter(Team.team_code == team_code).one_or_none()
    if team is None:
        team = Team(team_code=team_code, team_name=team_name)
        session.add(team)
        session.flush()
    return team


def _seed_season_center_data() -> None:
    session_factory = get_session_factory()
    with session_factory() as session:
        ss = _get_or_create_team(session, "SS", "삼성 라이온즈")
        lg = _get_or_create_team(session, "LG", "LG 트윈스")

        games = [
            Game(
                kbo_game_id="20260401SSLG0",
                game_date=date(2026, 4, 1),
                status_code="3",
                stadium="대구",
                season_id=2026,
                le_id=1,
                sr_id=0,
                away_team_id=lg.id,
                home_team_id=ss.id,
                away_score=2,
                home_score=5,
            ),
            Game(
                kbo_game_id="20260402SSLG0",
                game_date=date(2026, 4, 2),
                status_code="3",
                stadium="잠실",
                season_id=2026,
                le_id=1,
                sr_id=0,
                away_team_id=ss.id,
                home_team_id=lg.id,
                away_score=4,
                home_score=4,
            ),
            Game(
                kbo_game_id="20260403SSLG0",
                game_date=date(2026, 4, 3),
                status_code="3",
                stadium="잠실",
                season_id=2026,
                le_id=1,
                sr_id=0,
                away_team_id=ss.id,
                home_team_id=lg.id,
                away_score=6,
                home_score=3,
            ),
            Game(
                kbo_game_id="20250401SSLG0",
                game_date=date(2025, 4, 1),
                status_code="3",
                stadium="잠실",
                season_id=2025,
                le_id=1,
                sr_id=0,
                away_team_id=ss.id,
                home_team_id=lg.id,
                away_score=1,
                home_score=2,
            ),
        ]
        session.add_all(games)
        session.flush()

        team_game_stats = [
            TeamGameStat(game_id=games[0].id, team_id=ss.id, runs=5, hits=9, errors=0, walks=4),
            TeamGameStat(game_id=games[0].id, team_id=lg.id, runs=2, hits=6, errors=1, walks=2),
            TeamGameStat(game_id=games[1].id, team_id=ss.id, runs=4, hits=8, errors=0, walks=3),
            TeamGameStat(game_id=games[1].id, team_id=lg.id, runs=4, hits=8, errors=0, walks=4),
            TeamGameStat(game_id=games[2].id, team_id=ss.id, runs=6, hits=10, errors=0, walks=5),
            TeamGameStat(game_id=games[2].id, team_id=lg.id, runs=3, hits=7, errors=1, walks=3),
            TeamGameStat(game_id=games[3].id, team_id=ss.id, runs=1, hits=5, errors=0, walks=1),
            TeamGameStat(game_id=games[3].id, team_id=lg.id, runs=2, hits=7, errors=0, walks=2),
        ]
        session.add_all(team_game_stats)

        batting_rows = []
        pitching_rows = []
        for game in games[:3]:
            batting_rows.extend(
                [
                    PlayerGameBattingStat(
                        game_id=game.id,
                        team_id=ss.id,
                        player_key="ss-구자욱",
                        player_name="구자욱",
                        batting_order=3,
                        position_code="RF",
                        plate_appearances=4,
                        at_bats=4,
                        runs=1,
                        hits=2,
                        doubles=1,
                        triples=0,
                        home_runs=0,
                        runs_batted_in=1,
                        walks=0,
                        hit_by_pitch=0,
                        sacrifice_flies=0,
                        strikeouts=1,
                    ),
                    PlayerGameBattingStat(
                        game_id=game.id,
                        team_id=lg.id,
                        player_key="lg-홍창기",
                        player_name="홍창기",
                        batting_order=1,
                        position_code="CF",
                        plate_appearances=4,
                        at_bats=4,
                        runs=1,
                        hits=1,
                        doubles=0,
                        triples=0,
                        home_runs=0,
                        runs_batted_in=0,
                        walks=0,
                        hit_by_pitch=0,
                        sacrifice_flies=0,
                        strikeouts=0,
                    ),
                    PlayerGameBattingStat(
                        game_id=game.id,
                        team_id=lg.id,
                        player_key="lg-오지환",
                        player_name="오지환",
                        batting_order=5,
                        position_code="SS",
                        plate_appearances=2,
                        at_bats=2,
                        runs=0,
                        hits=1,
                        doubles=1,
                        triples=0,
                        home_runs=0,
                        runs_batted_in=1,
                        walks=0,
                        hit_by_pitch=0,
                        sacrifice_flies=0,
                        strikeouts=1,
                    ),
                ]
            )

            pitching_rows.extend(
                [
                    PlayerGamePitchingStat(
                        game_id=game.id,
                        team_id=ss.id,
                        player_key="ss-원태인",
                        player_name="원태인",
                        innings_outs=18,
                        batters_faced=24,
                        pitches_thrown=92,
                        at_bats=20,
                        hits_allowed=5,
                        home_runs_allowed=0,
                        walks_allowed=1,
                        strikeouts=7,
                        runs_allowed=2,
                        earned_runs=2,
                    ),
                    PlayerGamePitchingStat(
                        game_id=game.id,
                        team_id=lg.id,
                        player_key="lg-엔스",
                        player_name="엔스",
                        innings_outs=15,
                        batters_faced=22,
                        pitches_thrown=88,
                        at_bats=18,
                        hits_allowed=6,
                        home_runs_allowed=1,
                        walks_allowed=2,
                        strikeouts=6,
                        runs_allowed=4,
                        earned_runs=4,
                    ),
                    PlayerGamePitchingStat(
                        game_id=game.id,
                        team_id=lg.id,
                        player_key="lg-문보경-불펜",
                        player_name="김진성",
                        innings_outs=3,
                        batters_faced=5,
                        pitches_thrown=21,
                        at_bats=4,
                        hits_allowed=1,
                        home_runs_allowed=0,
                        walks_allowed=0,
                        strikeouts=1,
                        runs_allowed=0,
                        earned_runs=0,
                    ),
                ]
            )

        session.add_all(batting_rows)
        session.add_all(pitching_rows)
        session.commit()


def test_list_seasons(client) -> None:
    _seed_season_center_data()

    response = client.get("/api/seasons")

    assert response.status_code == 200
    assert response.json()["seasons"] == [2026, 2025]


def test_get_season_snapshot(client) -> None:
    _seed_season_center_data()

    response = client.get("/api/seasons/2026/snapshot")

    assert response.status_code == 200
    data = response.json()
    assert data["season"] == 2026
    assert data["standings"][0]["team_code"] == "SS"
    assert data["standings"][0]["wins"] == 2
    assert data["standings"][0]["draws"] == 1
    assert data["standings"][0]["hits"] == 27
    assert data["standings"][0]["games_back"] == 0.0
    assert data["standings"][0]["stolen_bases"] == 0
    hitter = next(item for item in data["players"] if item["player_id"] == "ss-구자욱")
    assert hitter["qualified_hitter"] is True
    assert hitter["hits"] == 6
    assert hitter["doubles"] == 3
    pitcher = next(item for item in data["players"] if item["player_id"] == "ss-원태인")
    assert pitcher["qualified_pitcher"] is True
    assert pitcher["era"] == 3.0
    assert pitcher["wins"] == 0


def test_missing_season_returns_not_found(client) -> None:
    response = client.get("/api/seasons/1999/snapshot")
    assert response.status_code == 404


def test_get_season_snapshot_with_series_code_filter(client) -> None:
    _seed_season_center_data()

    response = client.get("/api/seasons/2026/snapshot", params={"series_code": "regular"})

    assert response.status_code == 200
    data = response.json()
    assert data["season"] == 2026
    assert data["snapshot_label"].endswith("regular db snapshot")
