# Data Pipeline

## Source Systems

초기 단계의 기본 원천 데이터 소스는 KBO 공식 홈페이지로 확정한다. 시즌 정보, 팀 기록, 선수 기록, 경기 결과, 경기별 raw 기록을 이 소스에서 우선 수집하는 것을 원칙으로 한다.

스크래핑 구현의 기본 라이브러리 후보는 Python `SCRAPLING` 으로 두며, 페이지별로 정적 fetch 와 동적 fetch 필요 여부를 구분해 적용한다.

## Collection Schedule

- 시즌 진행 중에는 하루 1회 스크래핑 작업을 실행한다.
- 당일 경기 종료 이후 데이터를 안정적으로 수집할 수 있는 시간대에 배치 실행을 목표로 한다.
- 비시즌에는 필요 시 수동 갱신 또는 낮은 빈도의 점검 실행으로 운영한다.

## Update Flow

1. 스케줄러가 일일 수집 작업을 시작한다.
2. KBO 일정/스코어보드 페이지에서 당일 경기 목록과 경기 식별자를 수집한다.
3. 팀 순위, 기록실, 선수 조회, 선수 이동 현황 같은 정적 페이지에서 시즌/프로필 데이터를 수집한다.
4. `GameCenter` 메타데이터(`/ws/Main.asmx`)와 section별 HTML partial 또는 리뷰 상세에서 경기별 상세 데이터를 수집한다.
5. 수집 데이터를 내부 표준 형식으로 정제한다.
6. 중복 여부와 기본 유효성을 검사한다.
7. PostgreSQL에 시즌 기록과 경기 기록을 저장 또는 갱신한다.
8. API에서 최신 데이터를 조회 가능하도록 반영 상태를 갱신한다.
9. 작업 결과를 로그에 남기고 마지막 성공 시점을 기록한다.

초기 구현 전에는 `docs/operations/kbo-source-inventory.md` 를 기준으로 어떤 페이지가 실제로 MVP에 필요한 필드를 제공하는지 검증해야 한다.
특히 `스코어보드` 는 정적 수집 우선 후보, `게임센터` 는 `ws/Main.asmx` + section별 partial HTML 구조를 검증해야 하는 동적 수집 대상이라는 구분을 명확히 유지한다.

## Failure Handling

- 수집 실패 시 전체 작업 실패 여부와 실패 구간을 로그로 남긴다.
- 일부 경기 또는 일부 엔티티만 실패한 경우 재시도 가능하도록 작업 단위를 분리하는 것이 바람직하다.
- 데이터 형식이 예상과 다를 경우 원천 응답과 파싱 오류를 함께 기록한다.
- 사용자 화면에는 마지막 성공 갱신 시점을 노출해 데이터 최신성을 설명할 수 있어야 한다.

## Execution Boundary

- MVP 단계에서는 스크래핑과 일일 적재를 하나의 ingestion 앱 경계에서 먼저 수행한다.
- 이 경계 내부에서는 최소한 source collection 책임과 batch orchestration 책임을 모듈 수준으로 분리한다.
- source collection 은 `ScoreBoard`, `GameCenter`, `Record`, `Player/Search`, `Player/Trade` 같은 원천 페이지 fetch 와 원문 캡처를 담당한다.
- batch orchestration 은 스케줄링, 재시도, 중복 검사, PostgreSQL upsert, 동기화 로그 기록을 담당한다.
- 수집 대상과 실행 정책이 복잡해질 경우 이후 `apps/scraper` 와 `apps/worker` 로 프로젝트를 분리한다.
