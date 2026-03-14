import json
from pathlib import Path

from app.ingest.parsers.scoreboard_parser import parse_scoreboard_payload


def test_parse_scoreboard_payload_extracts_meta_and_innings() -> None:
    fixture_path = Path(__file__).parent / "fixtures" / "kbo" / "scoreboard_20260314WONC0.json"
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))

    parsed = parse_scoreboard_payload(payload, status_code="3")

    assert parsed.game_id == "20260314WONC0"
    assert parsed.away_team.team_code == "WO"
    assert parsed.home_team.team_code == "NC"
    assert parsed.away_team.runs == 6
    assert parsed.home_team.runs == 8
    assert len(parsed.innings) == 9
    assert parsed.innings[0].away_runs == 0
    assert parsed.innings[0].home_runs == 2
    assert parsed.innings[7].away_runs == 1
    assert parsed.innings[7].home_runs == 1
