import argparse
import json
from pathlib import Path

from app.db.session import get_session_factory
from app.ingest.orchestrators.ingest_game import ingest_single_game


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m app.ingest.cli")
    subparsers = parser.add_subparsers(dest="command", required=True)

    ingest_parser = subparsers.add_parser("ingest-game", help="Ingest one completed KBO game")
    ingest_parser.add_argument("--game-date", required=True)
    ingest_parser.add_argument("--game-id", required=True)
    ingest_parser.add_argument("--fixture-dir", default="apps/api/tests/fixtures/kbo")
    ingest_parser.add_argument("--use-live", action="store_true")
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


if __name__ == "__main__":
    main()
