import json
from pathlib import Path

from app.ingest.parsers.review_parser import parse_boxscore_payload


def test_parse_boxscore_payload_extracts_batting_and_pitching_rows() -> None:
    fixture_path = Path(__file__).parent / "fixtures" / "kbo" / "boxscore_20260314WONC0.json"
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))

    parsed = parse_boxscore_payload(payload, away_team_code="WO", home_team_code="NC")

    assert len(parsed.batting_rows) == 6
    assert len(parsed.pitching_rows) == 4

    anchi = next(item for item in parsed.batting_rows if item.player_name == "안치홍")
    assert anchi.player_key == "wo-안치홍"
    assert anchi.doubles == 1
    assert anchi.home_runs == 1
    assert anchi.walks == 1
    assert anchi.at_bats == 4
    assert anchi.hits == 3

    kim = next(item for item in parsed.pitching_rows if item.player_name == "김녹원")
    assert kim.innings_outs == 8
    assert kim.walks_allowed == 4
    assert kim.strikeouts == 2
