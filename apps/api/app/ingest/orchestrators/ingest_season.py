from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

from sqlalchemy.orm import Session

from app.ingest.http_client import FixtureClient, KBOClient
from app.ingest.orchestrators.ingest_game import ingest_single_game

SERIES_GROUP_SR_IDS: dict[str, set[int]] = {
    "preseason": {1},
    "regular": {0},
    "postseason": {3, 4, 5, 7},
}


@dataclass(slots=True)
class SeasonIngestSummary:
    season: int
    requested_groups: list[str]
    scanned_dates: int
    matched_games: int
    ingested_games: int
    skipped_games: int
    failed_games: int


def infer_series_group(sr_id: int) -> str | None:
    for group, ids in SERIES_GROUP_SR_IDS.items():
        if sr_id in ids:
            return group
    return None


def ingest_season(
    session: Session,
    season: int,
    series_groups: list[str],
    fixture_dir: Path | None = None,
    use_live: bool = False,
    start_date: date | None = None,
    end_date: date | None = None,
) -> SeasonIngestSummary:
    if not series_groups:
        raise ValueError("at least one series group is required")

    client: FixtureClient | KBOClient = KBOClient() if use_live else FixtureClient(fixture_dir or Path("tests/fixtures/kbo"))
    requested_sr_ids = {sr_id for group in series_groups for sr_id in SERIES_GROUP_SR_IDS[group]}
    scanned_dates = 0
    matched_games = 0
    ingested_games = 0
    skipped_games = 0
    failed_games = 0

    current = start_date or date(season, 1, 1)
    last = end_date or date(season, 12, 31)

    while current <= last:
        scanned_dates += 1
        game_date = current.strftime("%Y%m%d")
        payload = client.fetch_game_list(game_date)
        games = payload.get("game", [])
        for item in games:
            sr_id = int(item.get("SR_ID", -1))
            le_id = int(item.get("LE_ID", -1))
            game_id = str(item.get("G_ID", ""))
            game_state = str(item.get("GAME_STATE_SC", ""))
            if le_id != 1 or sr_id not in requested_sr_ids or not game_id or game_state != "3":
                continue
            matched_games += 1
            if int(item.get("SEASON_ID", season)) != season:
                skipped_games += 1
                continue
            try:
                ingest_single_game(
                    session=session,
                    game_date=game_date,
                    game_id=game_id,
                    fixture_dir=fixture_dir,
                    use_live=use_live,
                )
                ingested_games += 1
            except Exception:
                failed_games += 1
        current += timedelta(days=1)

    return SeasonIngestSummary(
        season=season,
        requested_groups=series_groups,
        scanned_dates=scanned_dates,
        matched_games=matched_games,
        ingested_games=ingested_games,
        skipped_games=skipped_games,
        failed_games=failed_games,
    )
