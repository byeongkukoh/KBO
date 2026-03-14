# Current Status

## Purpose

이 문서는 다른 컴퓨터나 새 세션에서 작업을 이어갈 때 가장 먼저 읽는 handoff 문서다. 현재까지 확정된 내용, 최근 완료 작업, 다음 우선순위 작업을 짧게 유지한다.

## Current Snapshot

- 저장소 구조는 monorepo 기준으로 `apps/web`, `apps/api`, `docs/` 로 정리되어 있다.
- 프로젝트 운영 규칙은 `RULES.md`, AI 저장소 가이드는 `AGENTS.md` 에 정리되어 있다.
- 프론트엔드는 React + TypeScript + Tailwind CSS, 백엔드는 Conda 기반 Python + FastAPI 로 스캐폴드가 완료된 상태다.
- 데이터베이스는 PostgreSQL 사용 예정이며, 초기 스키마 초안을 `docs/data/postgresql-schema-outline.md` 에 정리했다.
- 수집 경계는 MVP 기준으로 단일 ingestion 앱을 우선하고, source collection 과 batch orchestration 책임을 내부 모듈로 나누는 방향으로 정리했다.

## Completed Planning Work

- 서비스 기획 기본 문서 작성 완료
  - `docs/product/service-overview.md`
  - `docs/product/information-architecture.md`
- 데이터 모델 및 통계 범위 문서 작성 완료
  - `docs/data/domain-model.md`
  - `docs/data/postgresql-schema-outline.md`
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
- `/Record/Player/HitterDetail/Basic.aspx?playerId={playerId}`
- `/Record/Retire/Hitter.aspx?playerId={playerId}`

확인된 사실:

- `ScoreBoard` 는 날짜별 경기, 상태, 회차별 점수, R/H/E/B, 승패투수, `gameId` 확보에 유용하다.
- `ScoreBoard` 리뷰 링크는 `/Schedule/GameCenter/Main.aspx?gameDate=...&gameId=...&section=REVIEW` 형식으로 연결된다.
- `GameCenter` 는 메인 shell + `/ws/Main.asmx/GetKboGameDate`, `/ws/Main.asmx/GetKboGameList` + section별 HTML partial 로딩 구조를 사용한다.
- 현재 확인된 `GameCenter` section 경로는 `Preview/StartPitcher.aspx`, `Preview/Team.aspx`, `Preview/LineUp.aspx`, `ReviewNew.aspx`, `KeyPlayerPitcher.aspx`, `KeyPlayerHitter.aspx`, `Highlight.aspx` 이다.
- `Player/Search` 는 선수 기본 프로필 필드를 제공한다.
- `Player/Search` 는 `/ws/Controls.asmx/GetSearchPlayer` 응답의 `P_LINK` 를 통해 현역은 `/Record/Player/HitterDetail/Basic.aspx?playerId=...`, 은퇴 선수는 `/Record/Retire/Hitter.aspx?playerId=...` 로 연결된다.
- 현역 선수 상세는 프로필 + `Basic`, `Total`, `Daily`, `Game`, `Situation`, `Award`, `SeasonReg` 탭 구조를 제공한다.
- `Player/Trade` 는 이동 이벤트 이력을 일정 수준까지 제공한다.
- `Record` 계열 페이지는 시즌별 기록과 다양한 세부 필터를 제공한다.
- PostgreSQL 초기 스키마는 경기/선수/팀/시즌 식별자와 시즌 기록, 경기 기록, source capture, sync log 중심으로 먼저 정리했다.
- ingestion 경계는 MVP 단계에서 단일 앱을 우선하고, source collection 과 batch orchestration 책임을 문서상 분리했다.

아직 구현 전 검증이 더 필요한 부분:

- play-by-play 수준의 `GameCenter` raw 이벤트 로그 요청 구조
- 현역 투수/은퇴 투수 상세 페이지가 타자 상세와 동일한 수준으로 수집 가능한지 여부
- 리그 평균 및 구장 보정 데이터 확보 방식
- 실제 요청 제한과 안정적인 배치 수집 범위

## Recommended Next Tasks

1. `GameCenter` 의 play-by-play 수준 raw 이벤트 로그 경로와 안정적인 배치 수집 범위를 추가 검증한다.
2. 현역 투수/은퇴 투수 상세 페이지의 필드 및 탭 구조를 타자 상세와 동일 기준으로 확인한다.
3. `postgresql-schema-outline.md` 를 기준으로 실제 테이블 구현 우선순위와 적재 순서를 확정한다.
4. MVP ingestion 앱 이름을 `apps/scraper` 와 `apps/worker` 중 어느 쪽으로 둘지 결정한다.

## Working Rule For Future Sessions

- 새 세션을 시작하면 먼저 이 문서를 읽고, 이어서 `AGENTS.md`, `RULES.md`, 관련 도메인 문서를 확인한다.
- 이 문서는 handoff 시점에만 보는 문서가 아니라 현재 작업 상태를 유지하는 기준 문서로 간주하고, 의미 있는 작업이 진행되거나 상태가 바뀔 때마다 계속 갱신한다.
- 작업을 멈추거나 마칠 때는 최소한 이 문서의 `Current Snapshot`, `Completed Planning Work`, `Recommended Next Tasks` 가 실제 상태와 다음 우선순위를 정확히 반영하는지 다시 확인한다.
