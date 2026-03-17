# Startup Checklist

## Purpose

이 문서는 다른 컴퓨터나 새 세션에서 OpenCode가 작업을 이어받을 때 반드시 확인해야 하는 시작 절차를 정리한다. 저장소를 처음 열었더라도 이 순서를 먼저 따르면 현재 상태와 다음 작업을 빠르게 복원할 수 있다.

## Session Start Order

1. `AGENTS.md` 를 읽는다.
2. `docs/continuation/current-status.md` 를 읽는다.
3. 필요하면 `RULES.md` 를 읽어 운영 규칙과 커밋 규칙을 다시 맞춘다.
4. 현재 작업 주제에 맞는 문서를 읽는다.
   - 화면/UX: `docs/product/service-overview.md`, `docs/product/information-architecture.md`
   - 데이터/지표: `docs/data/domain-model.md`, `docs/data/statistics-catalog.md`, `docs/data/advanced-metric-dependencies.md`
   - 수집/배치: `docs/operations/data-pipeline.md`, `docs/operations/kbo-source-inventory.md`
5. 실제 실행이 필요한 작업이면 로컬 환경 상태를 확인한다.

## Environment Checks

- PostgreSQL 컨테이너가 켜져 있는가?
- `conda activate kbo-record-api` 가 가능한가?
- `DATABASE_URL` 이 PostgreSQL 을 가리키는가?
- `alembic -c alembic.ini upgrade head` 가 적용됐는가?
- 프론트가 필요하면 `apps/web` 의 dependency 와 dev server 상태를 확인한다.

## Current Live Expectations

현재 기준으로 다른 세션에서도 먼저 확인해야 하는 사실은 다음과 같다.

- 시즌 API는 `/api/seasons` 기준으로 `2026`, `2025`, `2024` 를 반환해야 한다.
- PostgreSQL `games` 테이블에는 다음 시즌 분포가 있어야 한다.
  - `2024`: preseason 46, regular 720, postseason 16
  - `2025`: preseason 42, regular 720, postseason 16
  - `2026`: preseason 25
- season center 프론트는 seeded mock 이 아니라 실제 API를 기준으로 동작한다.

## Handoff Rule

- 의미 있는 작업이 끝나면 반드시 `docs/continuation/current-status.md` 를 갱신한다.
- 다음 세션에서 바로 이어야 할 작업이 있다면, 무엇을 확인했고 무엇이 아직 provisional 인지 적는다.
- 다른 컴퓨터로 옮겨 작업할 때는 새 세션이 이 문서와 `current-status.md` 를 먼저 읽는 것을 전제로 한다.

## If Something Looks Wrong

- 기대한 시즌이 API에 안 보이면 먼저 PostgreSQL `games` 분포와 `DATABASE_URL` 을 확인한다.
- 프론트에서 데이터가 안 뜨면 backend 프로세스가 최신 코드로 다시 실행됐는지 확인한다.
- season center 에서 특정 시즌/시리즈가 비어 있어도 UI는 empty state 로 유지되는 것이 정상이다.
