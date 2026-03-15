from dataclasses import dataclass
import re
from typing import Any

from app.ingest.parsers.common import build_player_key, parse_innings_to_outs, parse_table_json, to_int


@dataclass(slots=True)
class PlayerBattingParsed:
    team_code: str
    player_key: str
    player_name: str
    batting_order: int
    position_code: str
    plate_appearances: int
    at_bats: int
    runs: int
    hits: int
    doubles: int
    triples: int
    home_runs: int
    stolen_bases: int
    runs_batted_in: int
    walks: int
    intentional_walks: int
    hit_by_pitch: int
    sacrifice_flies: int
    strikeouts: int


@dataclass(slots=True)
class PlayerPitchingParsed:
    team_code: str
    player_key: str
    player_name: str
    innings_outs: int
    batters_faced: int
    pitches_thrown: int
    at_bats: int
    hits_allowed: int
    home_runs_allowed: int
    walks_allowed: int
    hit_by_pitch_allowed: int
    strikeouts: int
    runs_allowed: int
    earned_runs: int
    decision_code: str | None


@dataclass(slots=True)
class ReviewParsed:
    batting_rows: list[PlayerBattingParsed]
    pitching_rows: list[PlayerPitchingParsed]


def _count_events(cells: list[str]) -> dict[str, int]:
    counts = {"doubles": 0, "triples": 0, "home_runs": 0, "walks": 0, "ibb": 0, "hbp": 0, "sf": 0, "strikeouts": 0}
    for cell in cells:
        text = cell.strip()
        if text in {"", "-", "&nbsp;"}:
            continue
        if "홈" in text:
            counts["home_runs"] += 1
        elif text.endswith("3") or "3루" in text or ("3" in text and ("안" in text or "루" in text)):
            counts["triples"] += 1
        elif text.endswith("2") or "2루" in text or ("2" in text and ("안" in text or "루" in text)):
            counts["doubles"] += 1
        if "고의4구" in text or "고의 4구" in text:
            counts["walks"] += 1
            counts["ibb"] += 1
        elif "4구" in text or "볼넷" in text:
            counts["walks"] += 1
        if "사구" in text:
            counts["hbp"] += 1
        if "희비" in text:
            counts["sf"] += 1
        if "삼진" in text:
            counts["strikeouts"] += 1
    return counts


def _parse_table_etc(raw: str) -> dict[str, str]:
    if not raw:
        return {}
    table = parse_table_json(raw)
    parsed: dict[str, str] = {}
    for row in table.get("rows", []):
        cells = row.get("row", [])
        if len(cells) < 2:
            continue
        key = str(cells[0].get("Text", "")).strip()
        value = str(cells[1].get("Text", "")).strip()
        if key:
            parsed[key] = value
    return parsed


def _extract_named_event_counts(raw_text: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    if not raw_text:
        return counts
    for name in re.findall(r"([가-힣A-Za-z]+)\([^)]*\)", raw_text):
        cleaned = name.strip()
        counts[cleaned] = counts.get(cleaned, 0) + 1
    return counts


def parse_boxscore_payload(payload: dict[str, Any], away_team_code: str, home_team_code: str) -> ReviewParsed:
    batting_rows: list[PlayerBattingParsed] = []
    pitching_rows: list[PlayerPitchingParsed] = []
    table_etc = _parse_table_etc(str(payload.get("tableEtc", "")))
    stolen_base_counts = _extract_named_event_counts(table_etc.get("도루", ""))

    for idx, team_code in enumerate([away_team_code, home_team_code]):
        batter_identity = parse_table_json(payload["arrHitter"][idx]["table1"])
        batter_events = parse_table_json(payload["arrHitter"][idx]["table2"])
        batter_summary = parse_table_json(payload["arrHitter"][idx]["table3"])

        for row_index, row in enumerate(batter_identity["rows"]):
            ident_cells = row["row"]
            summary_cells = batter_summary["rows"][row_index]["row"]
            event_cells = [cell["Text"] for cell in batter_events["rows"][row_index]["row"]]
            event_counts = _count_events(event_cells)

            player_name = str(ident_cells[2]["Text"]).strip()
            batting_rows.append(
                PlayerBattingParsed(
                    team_code=team_code,
                    player_key=build_player_key(team_code, player_name),
                    player_name=player_name,
                    batting_order=to_int(ident_cells[0]["Text"]),
                    position_code=str(ident_cells[1]["Text"]).strip(),
                    plate_appearances=sum(1 for cell in event_cells if cell not in {"", "-", "&nbsp;"}),
                    at_bats=to_int(summary_cells[0]["Text"]),
                    hits=to_int(summary_cells[1]["Text"]),
                    runs_batted_in=to_int(summary_cells[2]["Text"]),
                    runs=to_int(summary_cells[3]["Text"]),
                    doubles=event_counts["doubles"],
                    triples=event_counts["triples"],
                    home_runs=event_counts["home_runs"],
                    stolen_bases=stolen_base_counts.get(player_name, 0),
                    walks=event_counts["walks"],
                    intentional_walks=event_counts["ibb"],
                    hit_by_pitch=event_counts["hbp"],
                    sacrifice_flies=event_counts["sf"],
                    strikeouts=event_counts["strikeouts"],
                )
            )

        pitcher_table = parse_table_json(payload["arrPitcher"][idx]["table"])
        for row in pitcher_table["rows"]:
            cells = row["row"]
            player_name = str(cells[0]["Text"]).strip()
            pitching_rows.append(
                PlayerPitchingParsed(
                    team_code=team_code,
                    player_key=build_player_key(team_code, player_name),
                    player_name=player_name,
                    innings_outs=parse_innings_to_outs(str(cells[6]["Text"])),
                    batters_faced=to_int(cells[7]["Text"]),
                    pitches_thrown=to_int(cells[8]["Text"]),
                    at_bats=to_int(cells[9]["Text"]),
                    hits_allowed=to_int(cells[10]["Text"]),
                    home_runs_allowed=to_int(cells[11]["Text"]),
                    walks_allowed=to_int(cells[12]["Text"]),
                    hit_by_pitch_allowed=0,
                    strikeouts=to_int(cells[13]["Text"]),
                    runs_allowed=to_int(cells[14]["Text"]),
                    earned_runs=to_int(cells[15]["Text"]),
                    decision_code=(str(cells[2]["Text"]).strip() or None),
                )
            )

    return ReviewParsed(batting_rows=batting_rows, pitching_rows=pitching_rows)
