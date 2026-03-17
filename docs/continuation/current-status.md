# Current Status

## Purpose

이 문서는 다른 컴퓨터나 새 세션에서 작업을 이어갈 때 가장 먼저 읽는 handoff 문서다. 현재까지 확정된 내용, 최근 완료 작업, 다음 우선순위 작업을 짧게 유지한다.

세션 시작 절차와 환경 확인 순서는 `docs/continuation/startup-checklist.md` 를 기준으로 한다.

## Current Snapshot

- 저장소 구조는 monorepo 기준으로 `apps/web`, `apps/api`, `docs/` 로 정리되어 있다.
- 프로젝트 운영 규칙은 `RULES.md`, AI 저장소 가이드는 `AGENTS.md` 에 정리되어 있다.
- 프론트엔드는 React + TypeScript + Tailwind CSS, 백엔드는 Conda 기반 Python + FastAPI 로 운영한다.
- `compose.yml` 에 PostgreSQL 개발 컨테이너 구성을 추가했고, API/ingest 는 호스트에서 실행하는 방식을 유지한다.
- `apps/api` 에 단일 경기 vertical slice 백엔드 구현이 추가되어 fixture 또는 live 소스로 1경기 ingest, PostgreSQL 저장, 파생 지표 계산, 조회 API 제공이 가능하다.
- `apps/api` 에 시즌 센터용 read API가 추가되어 기존 game-level 테이블에서 시즌별 팀 순위/팀 통계/선수 리더보드를 DB 집계로 조회할 수 있다.
- 2024 전체 시즌(46/720/16), 2025 전체 시즌(42/720/16), 2026 오늘 기준 preseason 25경기 데이터가 PostgreSQL 에 적재되어 시즌별/시리즈별 조회가 가능하다.
- `apps/web` 시즌 센터 프론트엔드가 실제 `GET /api/seasons` / `GET /api/seasons/{season}/snapshot` API를 사용하도록 전환되어 팀 순위, 팀 통계, 선수 Top 5, 전체 선수 기록 화면을 DB snapshot 기준으로 조회한다.
- 시즌 센터 프론트/백엔드 구조를 기능 단위 모듈로 분리해 유지보수성을 개선했다.
- 시즌 센터는 이제 URL query state, 전체 기록 페이지네이션, 선수 상세 페이지를 포함한 실제 탐색 흐름을 지원한다.
- 시즌 센터 URL 구조는 `/seasons/:season`, `/seasons/:season/players`, `/seasons/:season/players/:playerKey` 기준으로 동작한다.
- 데이터가 없는 시즌/시리즈를 선택해도 시즌 센터 컨트롤을 유지한 채 empty state 로 복구되도록 프론트 UX를 보강했다.
- 시즌 센터와 선수 상세에 sabermetrics v1 지표가 추가되어 저위험 파생 지표를 실제 2025 시즌 데이터 기준으로 확인할 수 있다.
- `docs/product/sabermetrics-ui-next-phase.md` 에 현재 UI의 사베르메트릭스 적합성 평가와 다음 단계 작업 분리를 정리했다.
- 선수 상세에 월별 split 그래프와 선수 비교 차트 UI를 추가해 일반 사용자도 월별 추이와 선수 간 차이를 시각적으로 볼 수 있다.
- 팀 상세 페이지와 경기 목록/상세 화면이 season center 흐름에 연결되었다.
- league baseline/상수 계층을 확장해 Tier 2 지표 일부(`wOBA`, `wRC`, `wRC+`, `FIP`)를 실제 API 응답에 포함하기 시작했다.
- season/team/game/player 응답에 freshness 메타데이터가 추가되어 마지막 적재 시점과 컨텍스트 갱신 시점을 함께 노출한다.

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
- 시즌 센터 필드 확장 완료
  - player game batting stats 에 `stolen_bases`, player game pitching stats 에 `decision_code` 저장
  - 시즌 snapshot 에서 팀 `stolen_bases`, 투수 `wins`, 타자 `stolen_bases` 집계 가능
- 시즌 센터 계산 및 구조 개선 완료
  - `games_back` 를 표준 경기차 식으로 수정
  - `parse_innings_to_outs` 가 `5.1`, `5.2` 같은 야구 이닝 표기를 올바르게 해석하도록 수정
  - 시즌 센터 백엔드를 standings/player records 모듈로 분리하고 전체 기록용 pagination API `GET /api/seasons/{season}/player-records` 추가
  - 프론트를 season-center feature 폴더와 view/component 단위로 분리하고, 전체 타자/투수 기록을 페이지네이션으로 조회하도록 확장
- 시즌 센터 탐색 UX 확장 완료
  - 전체 기록 화면에 page size 선택, 직접 페이지 이동, URL query state 동기화 추가
  - `GET /api/players/{player_key}/season-detail` 추가로 선수 상세 페이지에서 시즌 요약과 경기 로그 페이지네이션 제공
  - 시즌 센터에서 선수명 클릭 시 실제 player detail view 로 이동 가능
  - player detail 은 커리어 시즌 요약 테이블 + 선택 시즌 게임 로그 형태로 확장
  - player detail 은 월별 split line chart 를 통해 타율/OPS/홈런/도루 등 월별 추이를 그래프로 표시
  - 전체 선수 기록 화면에는 선수 비교 패널을 추가해 radar chart 와 월별 비교 line chart 를 제공
- sabermetrics v1 추가 완료
  - 타자: `ISO`, `BABIP`, `BB%`, `K%`
  - 투수: `WHIP`, `K/9`, `BB/9`, `K/BB`
  - 시즌 snapshot, player-records, player-detail 응답과 프론트 전체 기록/선수 상세 화면에 공통 반영
  - 고급 지표 Tier 2 전 단계로, 리그 평균/상수 데이터 없이 계산 가능한 저위험 파생 지표만 우선 노출
- 팀/경기 탐색 1차 구현 완료
  - `GET /api/teams/{team_code}/season-detail` 추가
  - `GET /api/games` 목록 API 추가
  - 프론트에서 팀 상세 화면, 경기 목록 화면, 경기 상세 화면을 season center path에 연결
- 서비스 hardening 1차 구현 완료
  - `/api/games` 는 SQL-side filter/pagination 으로 전환
  - season snapshot / player-records / player-detail / team-detail / game-list / game-detail 에 freshness 응답 추가
  - 프론트 shell 이 freshness 정보를 보여주도록 갱신
- 멀티 시즌 적재 및 정시 동기화 구현 완료
  - 2024 시즌: preseason 46, regular 720, postseason 16 적재 완료
  - 2026 시즌: preseason 25 적재 완료
  - `/api/seasons` 응답은 현재 `[2026, 2025, 2024]`
  - `python -m app.ingest.cli run-scheduled-season-sync ...` 로 지정 시각 정시 동기화 가능
- 리그 baseline/상수 1차 구현 완료
  - `league_season_batting_contexts`, `league_season_pitching_contexts`, `advanced_metric_constants` 테이블 추가
  - `python -m app.ingest.cli refresh-league-context --season 2025 --series-code regular` 지원
  - 팀 상세에서 `OPS+`, `ERA+` 를 첫 Tier 2 지표로 노출
- Tier 2 지표 1차 확장 완료
  - raw input 확장: `intentional_walks`, `hit_by_pitch_allowed`
  - league context refresh 시 `LEAGUE_WOBA`, `LEAGUE_R_PER_PA`, `FIP_CONSTANT` 등 provisional season constants 저장
  - 시즌 snapshot / player-records / player-detail 에 `wOBA`, `wRC`, `wRC+`, `FIP` 노출
  - 현재 `IBB`, pitcher `HBP allowed` 는 source 제약으로 대부분 0 기반이며, constants 는 season-derived provisional 값이다.
- 선수 비교/그래프 기능 1차 구현 완료
  - `GET /api/players/{player_key}/season-detail` 응답에 `monthly_splits` 추가
  - `GET /api/players/compare` 추가
  - 프론트는 `Recharts` 기반 `LineChart` / `RadarChart` 로 월별 추이와 선수 비교를 렌더링
- 2025 실제 시즌 적재 완료
  - `python -m app.ingest.cli ingest-season --season 2025 --series-group preseason --series-group regular --series-group postseason --use-live --start-date 2025-03-01 --end-date 2025-10-31` 실행
  - 적재 결과: preseason 42경기, regular 720경기, postseason 16경기, 총 778경기 성공
  - 시즌 적재 중 중복 선수 행을 병합하도록 ingest 로직을 보강해 bulk backfill 실패를 제거
- 2024 / 2026 실제 시즌 적재 완료
  - 2024: preseason 46경기, regular 720경기, postseason 16경기, 총 782경기 적재 성공
  - 2026: 현재까지 완료된 preseason 25경기 적재 성공
  - `/api/seasons` 응답은 현재 `[2026, 2025, 2024]`
- 2026-03-17 기준 DB 재적재 완료
  - PostgreSQL 데이터를 다시 올리기 위해 `conda run -n kbo-record-api` 기준으로 의존성 설치, Alembic upgrade, 2024/2025/2026 live season ingest 를 재실행했다.
  - 검증 결과 `games` 분포는 2024 `46/720/16`, 2025 `42/720/16`, 2026 `25/0/0` 이고, query service 기준 `list_available_seasons()` 는 `[2026, 2025, 2024]` 를 반환한다.
  - league context 는 2024/2025 preseason·regular·postseason, 2026 preseason 기준으로 다시 refresh 했다.
- 정시 시즌 동기화 명령 추가
  - `python -m app.ingest.cli run-scheduled-season-sync --season 2026 --series-group preseason --series-group regular --time 09:00 --time 21:00 --timezone Asia/Seoul --lookback-days 3 --use-live`
  - 지정 시각마다 최근 `lookback_days` 범위를 다시 훑어 완료된 경기를 적재하고 league context 를 갱신한다.
- 프론트엔드 season center 실제 API 전환 완료
  - `apps/web/src/App.tsx` 에서 시즌 목록과 시즌 snapshot 을 비동기 fetch 하도록 전환
  - `apps/web/src/lib/api.ts` 에 season API adapter 추가
  - Playwright smoke 테스트를 실제 `/api/seasons*` 요청 interception 기준으로 갱신
  - 전체 보기 화면은 `/api/seasons/{season}/player-records` 를 통해 hitter/pitcher 별 페이지네이션 조회를 수행

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
- 현재 프론트 standings/player records 화면은 실제 백엔드 season snapshot API를 기준으로 동작한다.
- 시즌 센터 백엔드는 현재 DB-backed snapshot 응답에서 팀 `stolen_bases`, 투수 `wins`, 타자 `stolen_bases` 를 실제 집계로 반환한다.
- 시즌 센터 백엔드는 현재 DB-backed snapshot/records 응답에서 `Games Back`, `WHIP`, `stolen_bases`, 투수 `wins` 를 실제 적재 데이터 기준으로 계산한다.
- 시즌 센터 백엔드는 현재 DB-backed snapshot/records/detail 응답에서 sabermetrics v1 (`ISO`, `BABIP`, `BB%`, `K%`, `K/9`, `BB/9`, `K/BB`) 을 실제 적재 데이터 기준으로 계산한다.
- 시즌 센터 백엔드는 현재 DB-backed snapshot/records/detail 응답에서 Tier 2 1차(`wOBA`, `wRC`, `wRC+`, `FIP`)를 provisional constants 기반으로 계산한다.
- 팀 상세는 현재 시즌 누적 기록, 최근 경기, `OPS+`, `ERA+` 를 제공한다.
- 경기 목록/상세는 현재 완료 경기 중심 탐색만 지원하며, raw play-by-play는 아직 제공하지 않는다.
- 현재 서비스는 최신성 메타데이터를 함께 보여주지만, 캐시/경량 materialization 없이 request-time 집계 비중이 여전히 남아 있다.
- 현재 player detail 페이지는 문서상의 장기 목표인 커리어 전체 타임라인 대신, 2025 실제 시즌 기준 요약 + 게임 로그 중심으로 먼저 제공한다.
- player detail 은 현재 적재된 시즌 범위 안에서 커리어 시즌 요약을 보여주며, 현재 데이터셋 기준으로는 2025 시즌이 중심이다.
- 2025 실제 시즌 적재는 현재 관측된 `ws` game list / scoreboard / boxscore 응답을 사용한 live path 로 수행되며, public HTML inventory 기반 전환은 후속 과제로 남아 있다.
- public HTML inventory 방향은 계속 `ScoreBoard` 기반 경기 식별/발견을 우선 후보로 두고, `ws/*` 는 detail fallback 으로 한정하는 쪽이 저장소 문서와 가장 잘 맞는다.
- 현재 ingest 코드는 `ScoreBoard.aspx` HTML에서 `gameId` discovery 를 먼저 시도하고, 날짜 불일치 또는 inventory 부족 시 `GetKboGameList` 로 fallback 하도록 정리되어 있다. 즉 방향은 HTML-first 이지만, KBO가 단순 GET에 현재 날짜 scoreboard 를 반환하는 한계 때문에 아직 완전 cutover 단계는 아니다.
- 현재 운영 기준 시즌 분포는 2024, 2025, 2026 이며, 2026 은 preseason만 적재된 상태다.
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

1. `ScoreBoard.aspx` 날짜 제어 방식을 더 확인해 HTML-first inventory를 완전 cutover 할 수 있는지 검증한다.
2. 로컬 conda 환경에서 ingest CLI, scheduled sync, FastAPI 실행 절차를 문서화한다.
3. `IBB`, pitcher `HBP` 를 더 정확히 확보할 수 있는 source path를 확인해 Tier 2 지표 정확도를 높인다.
4. park factor / 리그별 weight 정책을 정해 `OPS+`, `ERA+`, `wRC+` 를 KBO 전용 기준으로 고도화한다.
5. season snapshot/player-records/player-detail/team-detail/game-list API에 캐싱 또는 경량 materialization 이 필요한지 측정한다.
6. 팀 상세와 시즌 센터에서 in-memory season aggregation 을 더 SQL/summary 친화적으로 줄일지 검토한다.
7. `docs/product/sabermetrics-ui-next-phase.md` 기준으로 glossary, baseline, comparison, split 확장 작업을 단계별로 구현한다.

## Working Rule For Future Sessions

- 새 세션을 시작하면 먼저 이 문서를 읽고, 이어서 `AGENTS.md`, `RULES.md`, 관련 도메인 문서를 확인한다.
- 이 문서는 handoff 시점에만 보는 문서가 아니라 현재 작업 상태를 유지하는 기준 문서로 간주하고, 의미 있는 작업이 진행되거나 상태가 바뀔 때마다 계속 갱신한다.
- 작업을 멈추거나 마칠 때는 최소한 이 문서의 `Current Snapshot`, `Completed Planning Work`, `Recommended Next Tasks` 가 실제 상태와 다음 우선순위를 정확히 반영하는지 다시 확인한다.
