import argparse
from dataclasses import asdict
import json
from datetime import date
from pathlib import Path

from app.db.session import get_session_factory
from app.ingest.orchestrators.ingest_game import ingest_single_game
from app.ingest.orchestrators.ingest_season import ingest_season
from app.services.league_context_service import refresh_league_context


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m app.ingest.cli")
    subparsers = parser.add_subparsers(dest="command", required=True)

    ingest_parser = subparsers.add_parser("ingest-game", help="Ingest one completed KBO game")
    ingest_parser.add_argument("--game-date", required=True)
    ingest_parser.add_argument("--game-id", required=True)
    ingest_parser.add_argument("--fixture-dir", default="apps/api/tests/fixtures/kbo")
    ingest_parser.add_argument("--use-live", action="store_true")

    season_parser = subparsers.add_parser("ingest-season", help="Ingest one KBO season by series group")
    season_parser.add_argument("--season", type=int, required=True)
    season_parser.add_argument(
        "--series-group",
        action="append",
        choices=["preseason", "regular", "postseason"],
        required=True,
        dest="series_groups",
    )
    season_parser.add_argument("--fixture-dir", default="apps/api/tests/fixtures/kbo")
    season_parser.add_argument("--use-live", action="store_true")
    season_parser.add_argument("--start-date")
    season_parser.add_argument("--end-date")

    context_parser = subparsers.add_parser("refresh-league-context", help="Refresh league baseline context for one season/series")
    context_parser.add_argument("--season", type=int, required=True)
    context_parser.add_argument("--series-code", choices=["preseason", "regular", "postseason"], required=True)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "ingest-game":
        session_factory = get_session_factory()
        with session_factory() as session:
            result = ingest_single_game(
                session=session,
                game_date=args.game_date,
                game_id=args.game_id,
                fixture_dir=Path(args.fixture_dir),
                use_live=bool(args.use_live),
            )
        print(json.dumps(result, ensure_ascii=False))
        return

    if args.command == "ingest-season":
        session_factory = get_session_factory()
        with session_factory() as session:
            result = ingest_season(
                session=session,
                season=args.season,
                series_groups=list(args.series_groups),
                fixture_dir=Path(args.fixture_dir),
                use_live=bool(args.use_live),
                start_date=date.fromisoformat(args.start_date) if args.start_date else None,
                end_date=date.fromisoformat(args.end_date) if args.end_date else None,
            )
        print(json.dumps(asdict(result), ensure_ascii=False))
        return

    if args.command == "refresh-league-context":
        session_factory = get_session_factory()
        with session_factory() as session:
            refresh_league_context(session=session, season=args.season, series_code=args.series_code)
            session.commit()
        print(json.dumps({"season": args.season, "series_code": args.series_code, "status": "refreshed"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
