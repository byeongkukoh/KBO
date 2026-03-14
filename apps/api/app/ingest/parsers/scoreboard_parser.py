from dataclasses import dataclass
from datetime import date
from typing import Any

from app.ingest.parsers.common import parse_table_json, to_int


@dataclass(slots=True)
class InningScoreParsed:
    inning_no: int
    away_runs: int
    home_runs: int


@dataclass(slots=True)
class TeamLineParsed:
    team_code: str
    team_name: str
    runs: int
    hits: int
    errors: int
    walks: int


@dataclass(slots=True)
class ScoreboardParsed:
    game_id: str
    game_date: date
    season_id: int
    le_id: int
    sr_id: int
    status_code: str
    stadium: str
    away_team: TeamLineParsed
    home_team: TeamLineParsed
    innings: list[InningScoreParsed]


def parse_scoreboard_payload(payload: dict[str, Any], status_code: str) -> ScoreboardParsed:
    inning_table = parse_table_json(payload["table2"])
    totals_table = parse_table_json(payload["table3"])

    inning_headers = [to_int(cell["Text"]) for cell in inning_table["headers"][0]["row"] if str(cell["Text"]).isdigit()]
    away_row = inning_table["rows"][0]["row"]
    home_row = inning_table["rows"][1]["row"]

    innings: list[InningScoreParsed] = []
    for idx, inning_no in enumerate(inning_headers):
        innings.append(
            InningScoreParsed(
                inning_no=inning_no,
                away_runs=to_int(away_row[idx]["Text"]),
                home_runs=to_int(home_row[idx]["Text"]),
            )
        )

    away_totals = totals_table["rows"][0]["row"]
    home_totals = totals_table["rows"][1]["row"]

    away = TeamLineParsed(
        team_code=payload["AWAY_ID"],
        team_name=str(payload["FULL_AWAY_NM"]),
        runs=to_int(away_totals[0]["Text"]),
        hits=to_int(away_totals[1]["Text"]),
        errors=to_int(away_totals[2]["Text"]),
        walks=to_int(away_totals[3]["Text"]),
    )
    home = TeamLineParsed(
        team_code=payload["HOME_ID"],
        team_name=str(payload["FULL_HOME_NM"]),
        runs=to_int(home_totals[0]["Text"]),
        hits=to_int(home_totals[1]["Text"]),
        errors=to_int(home_totals[2]["Text"]),
        walks=to_int(home_totals[3]["Text"]),
    )

    return ScoreboardParsed(
        game_id=payload["G_ID"],
        game_date=date.fromisoformat(payload["G_DT"]),
        season_id=to_int(payload["SEASON_ID"]),
        le_id=to_int(payload["LE_ID"]),
        sr_id=to_int(payload["SR_ID"]),
        status_code=status_code,
        stadium=str(payload["S_NM"]),
        away_team=away,
        home_team=home,
        innings=innings,
    )
