# Current Status

## Purpose

이 문서는 다른 컴퓨터나 새 세션에서 작업을 이어갈 때 가장 먼저 읽는 handoff 문서다. 현재까지 확정된 내용, 최근 완료 작업, 다음 우선순위 작업을 짧게 유지한다.

## Current Snapshot

- 저장소 구조는 monorepo 기준으로 `apps/web`, `apps/api`, `docs/` 로 정리되어 있다.
- 프로젝트 운영 규칙은 `RULES.md`, AI 저장소 가이드는 `AGENTS.md` 에 정리되어 있다.
- 프론트엔드는 React + TypeScript + Tailwind CSS, 백엔드는 Conda 기반 Python + FastAPI 로 운영한다.
- `compose.yml` 에 PostgreSQL 개발 컨테이너 구성을 추가했고, API/ingest 는 호스트에서 실행하는 방식을 유지한다.
- `apps/api` 에 단일 경기 vertical slice 백엔드 구현이 추가되어 fixture 또는 live 소스로 1경기 ingest, PostgreSQL 저장, 파생 지표 계산, 조회 API 제공이 가능하다.
- `apps/api` 에 시즌 센터용 read API가 추가되어 기존 game-level 테이블에서 시즌별 팀 순위/팀 통계/선수 리더보드를 DB 집계로 조회할 수 있다.
- `apps/web` 에 seeded preview 기반 시즌 센터 프론트엔드가 추가되어 팀 순위, 팀 통계, 선수 Top 5, 전체 선수 기록 화면을 단일 앱 셸에서 확인할 수 있다.

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
- 백엔드 최소 vertical slice 구현 완료
  - Alembic 초기 마이그레이션, SQLAlchemy 모델, ingest CLI(`python -m app.ingest.cli ingest-game`), fixture 기반 파서/적재/API 테스트 추가
  - API 엔드포인트 `GET /api/games/{game_id}`, `GET /api/players/{player_key}/summary?scope=ingested` 추가
- 백엔드 시즌 센터 read API 구현 완료
  - API 엔드포인트 `GET /api/seasons`, `GET /api/seasons/{season}/snapshot` 추가
  - game-level DB 테이블을 기반으로 standings, team stats, leaderboard player snapshot 집계 서비스 추가
  - conda 환경 `kbo-record-api` 생성, editable 설치, pytest, Alembic upgrade, PostgreSQL 연결 검증 완료
- 프론트엔드 seeded season center 구현 완료
  - `apps/web/src/App.tsx` 를 홈/선수 기록 앱 셸로 교체하고, 시즌 드롭다운, 팀 순위/팀 통계, 선수 Top 5, 전체 보기, 정규타석/정규이닝 필터를 local seeded contract로 구현
  - `apps/web/src/data/seededRecords.ts`, `apps/web/src/lib/records.ts`, `apps/web/src/types/records.ts` 추가
  - Playwright smoke 테스트를 seeded season center 기준으로 갱신

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
- `ReviewNew.aspx` 는 다시 `/ws/Schedule.asmx/GetScoreBoardScroll`, `/ws/Schedule.asmx/GetBoxScoreScroll` 호출에 의존하고, 키플레이어/하이라이트도 `ws/Schedule.asmx` 보조 호출 흔적이 보인다.
- 현재 vertical slice fixture는 공개 HTML만이 아니라 관측된 `ws/*` 응답 구조를 저장한 JSON fixture를 acceptance 기준으로 사용한다.
- `Player/Search` 는 선수 기본 프로필 필드를 제공한다.
- `Player/Search` 는 `/ws/Controls.asmx/GetSearchPlayer` 응답의 `P_LINK` 를 통해 현역은 `/Record/Player/HitterDetail/Basic.aspx?playerId=...`, 은퇴 선수는 `/Record/Retire/Hitter.aspx?playerId=...` 로 연결된다.
- 현역 선수 상세는 프로필 + `Basic`, `Total`, `Daily`, `Game`, `Situation`, `Award`, `SeasonReg` 탭 구조를 제공한다.
- `Player/Trade` 는 이동 이벤트 이력을 일정 수준까지 제공한다.
- `Record` 계열 페이지는 시즌별 기록과 다양한 세부 필터를 제공한다.
- 현재 프론트 standings/player records 화면은 실제 백엔드 API가 아니라 seeded snapshot contract를 기준으로 동작한다.
- 시즌 센터 백엔드는 현재 DB-backed snapshot 응답을 제공하지만, `stolen_bases` 와 투수 `wins` 는 현재 스키마에 없어 `null` 로 반환한다.
- PostgreSQL 초기 스키마는 경기/선수/팀/시즌 식별자와 시즌 기록, 경기 기록, source capture, sync log 중심으로 먼저 정리했다.
- ingestion 경계는 MVP 단계에서 단일 앱을 우선하고, source collection 과 batch orchestration 책임을 문서상 분리했다.
- `robots.txt` 는 `/ws/` 경로를 disallow 하고, `ScoreBoard` 의 문자중계 버튼은 로그인 경고로 연결된다.
- 따라서 현재 기준으로 공개적으로 검증된 경기 상세 원천은 박스스코어/리뷰/키플레이어/하이라이트 계층까지이며, 로그인 없이 접근 가능한 play-by-play 텍스트 이벤트 로그는 아직 확인하지 못했다.

아직 구현 전 검증이 더 필요한 부분:

- play-by-play 수준의 `GameCenter` raw 이벤트 로그 요청 구조
- `ws/*` 경로를 정책상 어느 범위까지 배치 수집 기본 경로로 사용할 수 있는지
- 현역 투수/은퇴 투수 상세 페이지가 타자 상세와 동일한 수준으로 수집 가능한지 여부
- 리그 평균 및 구장 보정 데이터 확보 방식
- 실제 요청 제한과 안정적인 배치 수집 범위

## Recommended Next Tasks

1. 프론트 season center를 seeded snapshot 대신 `GET /api/seasons/{season}/snapshot` 기반으로 전환한다.
2. `stolen_bases`, 투수 `wins` 처럼 현재 `null` 로 남는 필드를 실제 source/schema로 확장할지 결정한다.
3. 로컬 conda 환경에서 ingest CLI와 FastAPI 실행 절차를 문서화한다.
4. fixture의 게임 수를 점진적으로 늘리면서 파서 안정성 회귀 테스트를 확장한다.

## Working Rule For Future Sessions

- 새 세션을 시작하면 먼저 이 문서를 읽고, 이어서 `AGENTS.md`, `RULES.md`, 관련 도메인 문서를 확인한다.
- 이 문서는 handoff 시점에만 보는 문서가 아니라 현재 작업 상태를 유지하는 기준 문서로 간주하고, 의미 있는 작업이 진행되거나 상태가 바뀔 때마다 계속 갱신한다.
- 작업을 멈추거나 마칠 때는 최소한 이 문서의 `Current Snapshot`, `Completed Planning Work`, `Recommended Next Tasks` 가 실제 상태와 다음 우선순위를 정확히 반영하는지 다시 확인한다.
