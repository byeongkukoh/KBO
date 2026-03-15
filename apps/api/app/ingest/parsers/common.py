import json
import re
from typing import Any


def parse_table_json(raw: str) -> dict[str, Any]:
    return json.loads(raw)


def to_int(value: Any) -> int:
    if isinstance(value, int):
        return value
    text = str(value).strip()
    if text in {"", "-", "&nbsp;"}:
        return 0
    return int(float(text))


def parse_innings_to_outs(value: str) -> int:
    text = value.strip()
    if text in {"", "-", "&nbsp;"}:
        return 0
    if " " in text:
        whole, frac = text.split(" ", 1)
        if "/" in frac:
            numerator, denominator = frac.split("/", 1)
            return int(whole) * 3 + int(numerator) * (3 // int(denominator))
    if "/" in text:
        numerator, denominator = text.split("/", 1)
        return int(numerator) * (3 // int(denominator))

    match = re.fullmatch(r"(\d+)\.(\d+)", text)
    if match:
        whole = int(match.group(1))
        frac = int(match.group(2))
        if frac in {0, 1, 2}:
            return whole * 3 + frac
        if frac == 3:
            return whole * 3 + 1
        if frac in {6, 7}:
            return whole * 3 + 2
        if frac == 9:
            return whole * 3 + 3
    return int(float(text)) * 3


def build_player_key(team_code: str, player_name: str) -> str:
    normalized = "".join(ch for ch in player_name.strip().lower() if ch.isalnum())
    return f"{team_code.lower()}-{normalized}"
