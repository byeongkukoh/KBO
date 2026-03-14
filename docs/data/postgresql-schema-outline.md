# PostgreSQL Schema Outline

## Goal

초기 PostgreSQL 스키마 초안은 현재까지 확인된 KBO 원천 페이지 구조를 기준으로 MVP 조회와 일일 배치 적재를 안정적으로 지원하는 데 목적이 있다. 이 문서는 테이블 구현 SQL 자체보다 저장 책임, 식별자 전략, 단계별 확장 범위를 먼저 정리한다.

## Scope Boundary

- 이 초안은 시즌 기록, 선수 프로필, 팀 기록, 경기 메타 정보, 회차별 점수, 경기별 선수/팀 기록, 동기화 로그를 우선 대상으로 한다.
- `GameCenter` 의 play-by-play raw 이벤트 경로는 아직 완전히 확정되지 않았으므로, `PlayEvent` 계층은 확장 대상로 유지하고 MVP 핵심 적재 대상에서 분리한다.
- 고급 지표는 `docs/data/advanced-metric-dependencies.md` 의 의존성이 충족될 때 별도 파생 계층으로 도입한다.

## Identifier Strategy

### External Source Keys

- `game_id`: KBO `ScoreBoard` 와 `GameCenter` 에서 확인되는 경기 식별자. 예: `20260314WONC0`
- `game_date`: `YYYYMMDD` 형식의 경기 날짜 파라미터. 예: `20260314`
- `player_id`: 선수 상세와 검색 링크에 사용되는 KBO 선수 식별자. 예: `62404`
- `team_code`: `SS`, `LG`, `WO`, `NC` 같은 KBO 팀 코드
- `season_id`: KBO 페이지와 내부 시즌 연계를 위한 연도 기준 식별자

### Internal Primary Keys

- 내부 PK는 `bigserial` 또는 이에 준하는 정수 키를 기본으로 두고, KBO 원천 식별자는 별도 unique 컬럼으로 유지한다.
- 외부 식별자는 바뀔 가능성이 낮은 연결 키로 보고, API 응답과 내부 FK 연결은 내부 PK를 기준으로 구성한다.
- 원천 재수집과 upsert를 위해 외부 식별자 unique 제약은 초기에 명확히 둔다.

## Core Table Families

### Reference Tables

- `seasons`
  - 시즌 연도, 상태, 시작일, 종료일
  - unique: `year`

- `teams`
  - 팀 코드, 공식 팀명, 약칭, 리그 구분, 홈 구장 기초 정보
  - unique: `team_code`

- `venues`
  - 구장명, 지역, 표준화 이름
  - 초기에는 선택 사항이지만 경기/팀 연결을 위해 분리 여지가 있다.

### Player Tables

- `players`
  - KBO `player_id`, 이름, 현재 팀 FK, 포지션, 투/타 유형, 생년월일, 신장, 체중, 출신교, 드래프트 정보, 입단 정보, 현역 여부
  - unique: `kbo_player_id`
  - 설명: 검색 페이지와 상세 페이지에서 확인되는 최신 프로필 기준 테이블

- `player_team_history`
  - 선수 FK, 팀 FK, 시작 시즌/종료 시즌 또는 기간 텍스트, 출처, 비고
  - 설명: 상세 페이지의 경력 문자열과 이동 이력을 구조화하기 위한 계층

- `player_movement_events`
  - 선수 FK, 팀 FK, 이벤트 날짜, 이벤트 유형, 비고, 원천 페이지 레코드 키
  - 설명: `Player/Trade.aspx` 기반의 이동 이벤트 저장용

### Game Tables

- `games`
  - KBO `game_id`, `game_date`, 시즌 FK, 홈/원정 팀 FK, 경기 상태, 경기 구분, 시리즈 구분, 시작 시각, 구장 FK 또는 구장명, 점수, 리뷰 URL, GameCenter URL
  - unique: `kbo_game_id`
  - 설명: `ScoreBoard` 와 `GameCenter` 메타데이터의 기준 테이블

- `game_scoreboards`
  - 경기 FK, 홈/원정 최종 점수, R/H/E/B 집계, 승/패/세이브 투수명 또는 선수 FK, 현재 이닝/공수 상태, 취소 코드
  - 설명: 스코어보드 요약 계층을 정규화해서 보관

- `inning_scores`
  - 경기 FK, 이닝 번호, 홈 점수, 원정 점수, 누적 스코어 계산용 필드 또는 순서 정보
  - unique: `(game_id, inning_no)`

- `game_source_pages`
  - 경기 FK, source_type(`scoreboard`, `gamecenter_main`, `review`, `preview_team`, `preview_lineup`, `key_player_pitcher` 등), source_url, fetched_at, parser_version, checksum, 원문 저장 위치 또는 스냅샷 참조
  - 설명: partial HTML 기반 수집 구조를 추적하기 위한 원천 캡처 메타데이터

### Statistics Tables

- `player_season_batting_stats`
  - 선수 FK, 시즌 FK, 팀 FK, 시리즈 구분, 기본 타격 누적 지표
  - unique: `(player_id, season_id, team_id, series_code)`

- `player_season_pitching_stats`
  - 선수 FK, 시즌 FK, 팀 FK, 시리즈 구분, 기본 투수 누적 지표
  - unique: `(player_id, season_id, team_id, series_code)`

- `team_season_stats`
  - 팀 FK, 시즌 FK, 시리즈 구분, 순위/승패/득실/주요 타격 및 투수 지표
  - unique: `(team_id, season_id, series_code)`

- `player_game_batting_stats`
  - 경기 FK, 선수 FK, 팀 FK, 타순, 포지션, 경기 단위 타격 지표
  - unique: `(game_id, player_id, team_id, stat_role)`

- `player_game_pitching_stats`
  - 경기 FK, 선수 FK, 팀 FK, 선발 여부, 이닝/실점/삼진 등 경기 단위 투구 지표
  - unique: `(game_id, player_id, team_id, stat_role)`

- `team_game_stats`
  - 경기 FK, 팀 FK, 팀 타격 요약, 팀 투구 요약, 에러, 잔루 등 팀 경기 지표
  - unique: `(game_id, team_id)`

### Derived / Operational Tables

- `derived_player_metrics`
  - 선수 FK, 시즌 FK, metric_code, metric_value, calculation_version, freshness timestamp
  - Tier 1 지표부터 시작하고 Tier 2 이상은 기준 데이터 확보 후 확장

- `data_sync_runs`
  - 실행 시작/종료 시각, 대상 날짜, 실행 상태, 실패 구간, 재시도 횟수, 마지막 성공 여부

- `data_sync_items`
  - 실행 FK, source_type, entity_type, external_key, status, error_message
  - 설명: 일부 경기/엔티티 재시도를 가능하게 하는 작업 단위 로그

## Recommended Normalization Rules

- 선수 프로필, 선수 시즌 기록, 선수 이동 이력은 분리 저장한다.
- 경기 메타 정보와 스코어보드 요약, 경기별 선수 기록, 회차별 점수는 별도 테이블로 둔다.
- 현역 선수 상세와 은퇴 선수 상세는 같은 `players` 기준으로 수렴하되, 프로필 완성도 차이는 nullable 컬럼과 source metadata로 처리한다.
- 원천 페이지 원문 저장은 대용량 본문을 전부 DB에 넣기보다 checksum + 저장 위치 참조 방식도 허용한다.

## Staged Raw Event Strategy

### MVP Stage

- `games`
- `game_scoreboards`
- `inning_scores`
- `player_game_batting_stats`
- `player_game_pitching_stats`
- `team_game_stats`
- `game_source_pages`

이 단계에서는 회차별 점수, 박스스코어, 리뷰/키플레이어/라인업 등 현재 확인된 partial 페이지까지를 우선 적재 대상으로 본다.

### Extension Stage

- `play_events`
  - 경기 FK, 이벤트 순서, 이닝, 공수, 타자 FK, 투수 FK, 이벤트 타입, 원문 설명, 주자 상태, 득점 상태, 파생 필드
  - unique: `(game_id, event_seq)`

`play_events` 는 실제 raw 이벤트 경로와 안정적인 수집 방법이 확인된 뒤 도입한다. 현재 문서 단계에서는 필요한 엔티티로 유지하되, 즉시 구현 전제는 두지 않는다.

## Unique Key and Upsert Rules

- `games.kbo_game_id` unique
- `players.kbo_player_id` unique
- `teams.team_code` unique
- `inning_scores(game_id, inning_no)` unique
- 시즌 누적 기록은 `(player_id or team_id, season_id, series_code, role)` 수준의 중복 방지 키를 둔다.
- 경기별 기록은 `(game_id, player_id, team_id, role)` 또는 `(game_id, team_id)` 기준으로 upsert 한다.
- 동기화 로그는 실행 단위와 항목 단위를 분리해 부분 실패를 추적한다.

## API-Oriented Read Model Hints

- 선수 상세 API는 `players` + `player_team_history` + `player_season_*_stats` 를 조합한다.
- 팀 상세 API는 `teams` + `team_season_stats` + 관련 `games` 요약을 조합한다.
- 경기 상세 API는 `games` + `game_scoreboards` + `inning_scores` + `player_game_*_stats` + `team_game_stats` 를 조합한다.
- `play_events` 가 도입되기 전까지는 경기 상세의 raw 영역을 inning/boxscore/review 중심으로 제한한다.

## Open Items Kept Intentionally

- `GameCenter` play-by-play raw 이벤트의 실제 요청 구조
- 리그 평균/구장 보정치 저장 방식
- 현역 투수 상세 및 은퇴 투수 상세의 필드 완성도 차이
- source raw payload를 DB 본문으로 둘지 외부 저장소 참조로 둘지

## Recommended Next Follow-Up

1. 이 스키마 초안을 `docs/data/domain-model.md` 와 교차 검토해 엔티티 정의와 용어를 맞춘다.
2. `games`, `players`, `player_team_history`, `team_season_stats`, `player_season_*`, `player_game_*`, `data_sync_runs` 우선순위로 MVP 적재 순서를 확정한다.
3. 스크래퍼/워커 경계 문서에서 어떤 계층이 `ws/Main.asmx`, partial HTML, 정적 페이지 수집을 맡는지 책임 분리를 정의한다.
