# Raw Game Vertical Slice Plan

## Goal

Implement one end-to-end vertical slice that proves this flow inside the existing monorepo:

1. ingest one completed KBO game's publicly accessible raw-ish data,
2. persist normalized rows in PostgreSQL running in Docker,
3. derive Tier 1 player statistics from stored game/player-game rows,
4. expose the data through FastAPI,
5. verify it in the React frontend.

This slice is intentionally narrow and does not attempt to implement the full product.

## Must Have

- Docker Postgres only; API and ingestion run from the host using the conda environment `kbo-record-api`
- fixture-first parser tests using checked-in public HTML samples
- one ingestion command for one game
- PostgreSQL schema and migrations for one-game ingestion
- idempotent ingest behavior
- one read API for game detail and one read API for ingested player summary
- one frontend verification screen
- automated verification via pytest, build, and Playwright

## Must Not Have

- no full play-by-play or text relay ingestion
- no dependence on hidden or unverified KBO endpoints for the first slice
- no scheduler, cron, worker split, queue, or retry framework
- no season-complete or career-complete player statistics
- no Tier 2 or Tier 3 advanced metrics
- no API/web Dockerization in the first slice

## Chosen Scope

- Source shape: one completed game captured from public KBO HTML fixtures
- Raw-ish data target: game metadata, inning lines, team totals, batting rows, pitching rows, source capture metadata
- Derived metrics target:
  - batting: singles, total bases, AVG, OBP, SLG, OPS
  - pitching: WHIP, K/9, BB/9, K/BB
- Data completeness label: ingested-games-only

## Architecture Decision

- Keep implementation inside `apps/api` for now
- Separate module responsibilities inside the same app:
  - source collection/parsing
  - orchestration/ingest
  - persistence/query
- Keep the frontend as a single verification page in `apps/web`

## Files To Add Or Update

### Infra

- `compose.yml`
- `apps/api/.env.example`
- `apps/api/environment.yml`
- `apps/api/pyproject.toml`
- `apps/api/requirements.txt`

### API backend

- `apps/api/app/core/config.py`
- `apps/api/app/db/base.py`
- `apps/api/app/db/session.py`
- `apps/api/app/models/team.py`
- `apps/api/app/models/game.py`
- `apps/api/app/models/stats.py`
- `apps/api/app/models/sync.py`
- `apps/api/app/services/derived_stats.py`
- `apps/api/app/services/game_query_service.py`
- `apps/api/app/api/routes/games.py`
- `apps/api/app/api/routes/players.py`
- `apps/api/app/main.py`

### Ingestion

- `apps/api/app/ingest/http_client.py`
- `apps/api/app/ingest/parsers/scoreboard_parser.py`
- `apps/api/app/ingest/parsers/review_parser.py`
- `apps/api/app/ingest/orchestrators/ingest_game.py`
- `apps/api/app/ingest/cli.py`

### Alembic

- `apps/api/alembic.ini`
- `apps/api/alembic/env.py`
- `apps/api/alembic/versions/<revision>_vertical_slice.py`

### Tests and fixtures

- `apps/api/tests/fixtures/kbo/scoreboard_20260314.html`
- `apps/api/tests/fixtures/kbo/review_20260314WONC0.html`
- `apps/api/tests/test_scoreboard_parser.py`
- `apps/api/tests/test_review_parser.py`
- `apps/api/tests/test_derived_stats.py`
- `apps/api/tests/test_ingest_cli.py`
- `apps/api/tests/test_game_routes.py`

### Frontend

- `apps/web/src/lib/api.ts`
- `apps/web/src/types/game.ts`
- `apps/web/src/components/GameVerificationPanel.tsx`
- `apps/web/src/App.tsx`
- `apps/web/e2e/vertical-slice.spec.ts`

## Data Model For This Slice

- `teams`
- `games`
- `inning_scores`
- `team_game_stats`
- `player_game_batting_stats`
- `player_game_pitching_stats`
- `game_source_pages`
- `data_sync_runs`
- `data_sync_items`

For the first slice, player rows may use a local game-level identity if the public fixture does not expose a stable player ID everywhere. A stable player identifier should be used where the fixture supports it, but cross-game identity resolution is out of scope.

## Execution Order

1. Add Docker Postgres and backend settings/dependencies
2. Add parser fixtures and failing parser/derived-stat tests
3. Add DB models, migration, and persistence tests
4. Implement ingest CLI and idempotent upsert behavior
5. Implement game/player read APIs and route tests
6. Implement frontend verification page and Playwright smoke test
7. Run full verification against Docker Postgres and local app processes

## Verification Requirements

- `docker compose up -d postgres`
- `conda run -n kbo-record-api pytest apps/api/tests`
- `conda run -n kbo-record-api alembic upgrade head`
- ingest command is idempotent when run twice against the same fixture
- `GET /api/games/{game_id}` returns the ingested game with inning lines and player rows
- `GET /api/players/{player_key}/summary?scope=ingested` returns Tier 1 metrics from stored rows
- `npm --prefix apps/web run build`
- Playwright smoke verifies the frontend renders the ingested game and a derived player metric

## Deferred Items

- play-by-play / text relay
- `/ws/*` driven ingestion as a required dependency for the first slice
- season rollups and career pages
- league-adjusted metrics
- worker/app split

## Atomic Commit Strategy

1. `build(api): conda와 postgres 개발 구성을 추가한다`
2. `test(api): kbo fixture 파서와 파생 지표 테스트를 추가한다`
3. `feat(api): 단일 경기 적재용 스키마와 저장소 계층을 추가한다`
4. `feat(api): 단일 경기 ingest와 조회 api를 구현한다`
5. `test(web): 검증 화면 smoke 테스트를 추가한다`
6. `feat(web): 단일 경기 검증 화면을 추가한다`
