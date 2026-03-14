import json
from pathlib import Path
from typing import Any

import httpx

from app.core.config import get_settings


class KBOClient:
    def __init__(self, timeout: float = 15.0) -> None:
        self.base_url = get_settings().kbo_base_url.rstrip("/")
        self.timeout = timeout

    def fetch_game_list(self, game_date: str) -> dict[str, Any]:
        return self._post_json(
            "/ws/Main.asmx/GetKboGameList",
            {"leId": "1", "srId": "0,1,3,4,5,6,7,9", "date": game_date},
        )

    def fetch_scoreboard(self, le_id: int, sr_id: int, season_id: int, game_id: str) -> dict[str, Any]:
        return self._post_json(
            "/ws/Schedule.asmx/GetScoreBoardScroll",
            {"leId": str(le_id), "srId": str(sr_id), "seasonId": str(season_id), "gameId": game_id},
        )

    def fetch_boxscore(self, le_id: int, sr_id: int, season_id: int, game_id: str) -> dict[str, Any]:
        return self._post_json(
            "/ws/Schedule.asmx/GetBoxScoreScroll",
            {"leId": str(le_id), "srId": str(sr_id), "seasonId": str(season_id), "gameId": game_id},
        )

    def _post_json(self, path: str, data: dict[str, str]) -> dict[str, Any]:
        with httpx.Client(base_url=self.base_url, timeout=self.timeout, headers={"X-Requested-With": "XMLHttpRequest"}) as client:
            response = client.post(path, data=data)
            response.raise_for_status()
            return response.json()


class FixtureClient:
    def __init__(self, fixture_dir: Path) -> None:
        self.fixture_dir = fixture_dir

    def fetch_game_list(self, game_date: str) -> dict[str, Any]:
        return self._read_json(f"game_list_{game_date}.json")

    def fetch_scoreboard(self, le_id: int, sr_id: int, season_id: int, game_id: str) -> dict[str, Any]:
        return self._read_json(f"scoreboard_{game_id}.json")

    def fetch_boxscore(self, le_id: int, sr_id: int, season_id: int, game_id: str) -> dict[str, Any]:
        return self._read_json(f"boxscore_{game_id}.json")

    def _read_json(self, file_name: str) -> dict[str, Any]:
        path = self.fixture_dir / file_name
        return json.loads(path.read_text(encoding="utf-8"))
