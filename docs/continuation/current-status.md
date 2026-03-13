# Current Status

## Purpose

이 문서는 다른 컴퓨터나 새 세션에서 작업을 이어갈 때 가장 먼저 읽는 handoff 문서다. 현재까지 확정된 내용, 최근 완료 작업, 다음 우선순위 작업을 짧게 유지한다.

## Current Snapshot

- 저장소 구조는 monorepo 기준으로 `apps/web`, `apps/api`, `docs/` 로 정리되어 있다.
- 프로젝트 운영 규칙은 `RULES.md`, AI 저장소 가이드는 `AGENTS.md` 에 정리되어 있다.
- 프론트엔드는 React + TypeScript + Tailwind CSS, 백엔드는 Conda 기반 Python + FastAPI 로 스캐폴드가 완료된 상태다.
- 데이터베이스는 PostgreSQL 사용 예정이지만 상세 스키마 구현은 아직 시작하지 않았다.

## Completed Planning Work

- 서비스 기획 기본 문서 작성 완료
  - `docs/product/service-overview.md`
  - `docs/product/information-architecture.md`
- 데이터 모델 및 통계 범위 문서 작성 완료
  - `docs/data/domain-model.md`
  - `docs/data/statistics-catalog.md`
  - `docs/data/advanced-metric-dependencies.md`
- 운영 및 수집 문서 작성 완료
  - `docs/operations/data-pipeline.md`
  - `docs/operations/kbo-source-inventory.md`
  - `docs/operations/release-checklist.md`

## Verified Decisions

- 기본 원천 데이터 소스는 KBO 공식 홈페이지다.
- 스크래핑 라이브러리 기본 후보는 Python `SCRAPLING` 이다.
- 선수 페이지는 커리어 기준 시즌별 기록 중심이다.
- 팀 페이지는 시즌별 누적 기록 중심이다.
- 경기 페이지는 가능한 한 raw한 경기 흐름 중심이다.
- 고급 지표는 즉시 계산 가능한 것과 추가 의존성이 필요한 것을 분리해 단계적으로 제공한다.

## KBO Site Verification Summary

직접 확인한 주요 진입점:

- `/Schedule/Schedule.aspx`
- `/Schedule/ScoreBoard.aspx`
- `/Schedule/GameCenter/Main.aspx`
- `/Record/Player/HitterBasic/Basic1.aspx`
- `/Record/TeamRank/TeamRank.aspx`
- `/Player/Search.aspx`
- `/Player/Trade.aspx`

확인된 사실:

- `ScoreBoard` 는 날짜별 경기, 상태, 회차별 점수, R/H/E/B, 승패투수, `gameId` 확보에 유용하다.
- `Player/Search` 는 선수 기본 프로필 필드를 제공한다.
- `Player/Trade` 는 이동 이벤트 이력을 일정 수준까지 제공한다.
- `Record` 계열 페이지는 시즌별 기록과 다양한 세부 필터를 제공한다.

아직 구현 전 검증이 더 필요한 부분:

- `GameCenter` raw 이벤트 로그 요청 구조
- 선수 상세/커리어 상세 페이지 구조
- 리그 평균 및 구장 보정 데이터 확보 방식
- 실제 요청 제한과 안정적인 배치 수집 범위

## Recommended Next Tasks

1. `GameCenter` 요청 구조를 분석해서 raw 이벤트 수집 가능 범위를 확정한다.
2. 선수 상세 페이지 또는 추가 프로필 페이지 URL 패턴을 확인한다.
3. PostgreSQL 기준의 초기 스키마 초안을 `docs/data/` 문서에 정리한다.
4. 수집기(`apps/scraper` 또는 `apps/worker`) 프로젝트 생성 여부를 결정한다.

## Working Rule For Future Sessions

- 새 세션을 시작하면 먼저 이 문서를 읽고, 이어서 `AGENTS.md`, `RULES.md`, 관련 도메인 문서를 확인한다.
- 의미 있는 작업이 끝나면 이 문서의 `Current Snapshot`, `Completed Planning Work`, `Recommended Next Tasks` 를 갱신한다.
