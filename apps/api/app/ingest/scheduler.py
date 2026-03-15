from __future__ import annotations

from datetime import date, datetime, time, timedelta
from pathlib import Path
from time import sleep
from zoneinfo import ZoneInfo

from app.db.session import get_session_factory
from app.ingest.orchestrators.ingest_season import ingest_season
from app.services.league_context_service import refresh_league_context


def run_daily_season_sync(
    *,
    season: int,
    series_groups: list[str],
    times: list[str],
    timezone_name: str,
    lookback_days: int,
    use_live: bool,
    fixture_dir: Path,
) -> None:
    zone = ZoneInfo(timezone_name)
    schedule_times = [_parse_clock(value) for value in times]
    session_factory = get_session_factory()

    while True:
        now = datetime.now(zone)
        next_run = _next_run_at(now, schedule_times)
        sleep_seconds = max((next_run - now).total_seconds(), 1)
        sleep(sleep_seconds)

        run_at = datetime.now(zone)
        start_date = (run_at.date() - timedelta(days=lookback_days)).isoformat()
        end_date = run_at.date().isoformat()
        with session_factory() as session:
            ingest_season(
                session=session,
                season=season,
                series_groups=series_groups,
                fixture_dir=fixture_dir,
                use_live=use_live,
                start_date=date.fromisoformat(start_date),
                end_date=date.fromisoformat(end_date),
            )
            for series_code in ["preseason", "regular", "postseason"]:
                refresh_league_context(session=session, season=season, series_code=series_code)
            session.commit()


def _parse_clock(value: str) -> time:
    hour, minute = value.split(":", 1)
    return time(hour=int(hour), minute=int(minute))


def _next_run_at(now: datetime, schedule_times: list[time]) -> datetime:
    candidates = []
    for clock in schedule_times:
        candidate = datetime.combine(now.date(), clock, tzinfo=now.tzinfo)
        if candidate <= now:
            candidate += timedelta(days=1)
        candidates.append(candidate)
    return min(candidates)
