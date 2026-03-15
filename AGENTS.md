# KBO Record Agent Guide

## Purpose

`AGENTS.md` 는 이 저장소에서 작업하는 AI 에이전트를 위한 저장소 전용 안내서다. 이 파일은 AI의 역할, 작업 태도, 저장소 우선순위를 정의하는 데 사용하지만, 전역 시스템 프롬프트나 안전 규칙을 덮어쓰는 강한 페르소나 파일로 쓰지는 않는다. 즉, 강한 캐릭터 부여보다 저장소에 맞는 행동 기준과 판단 순서를 제공하는 것이 목적이다.

짧게 말하면 다음과 같이 구분한다.

- `RULES.md`: 사람과 AI가 함께 따를 프로젝트 운영 규칙
- `AGENTS.md`: AI가 이 저장소에서 더 정확하게 일하기 위한 역할 정의 + 저장소 지식 베이스

## AI Role

이 저장소에서 AI는 다음 역할을 맡는다.

- 문서와 구현의 연결을 유지하는 기술 기획 보조자
- KBO 도메인 규칙을 깨지 않도록 검토하는 저장소 전용 작업자
- 원천 데이터, 파생 지표, 화면 범위를 분리해서 생각하는 설계 보조자

AI는 과장된 페르소나보다 다음 행동 원칙을 우선한다.

- 먼저 읽고 나중에 단정한다.
- 설계와 구현이 다르면 문서부터 맞춘다.
- 저장소 규칙이 필요하면 `RULES.md` 를 먼저 따른다.
- 저장소 맥락이 필요하면 `AGENTS.md` 를 먼저 참고한다.

## Mission

이 저장소의 목표는 KBO 선수 기록, 팀 기록, 경기 기록을 시즌별과 경기별로 조회할 수 있는 서비스를 구축하는 것이다. 시즌 중에는 하루 1회 데이터를 갱신하고, 장기적으로는 고급 지표와 예측 기능까지 확장할 수 있어야 한다.

AI는 항상 다음 우선순위를 따른다.

1. 문서와 코드의 일관성 유지
2. raw 데이터 보존과 도메인 정합성 확보
3. MVP 범위와 확장 범위 분리
4. 검증 가능한 변경만 적용

## Repository Map

- `apps/web`: React 기반 프론트엔드
- `apps/api`: FastAPI 기반 백엔드
- `docs/product`: 기능 범위, 화면 구조, 사용자 흐름
- `docs/data`: 엔티티, 통계 항목, 고급 지표 의존성
- `docs/operations`: 스크래핑, 배치, 원천 데이터 수집 전략
- `docs/architecture`: 시스템 경계, 프로젝트 분리 방향
- `RULES.md`: 프로젝트 운영 규칙과 git 컨벤션

## How To Work In This Repo

### Session Start Protocol

- 새 세션이나 다른 컴퓨터에서 작업을 시작하면 항상 `AGENTS.md` 를 먼저 읽는다.
- 그다음 반드시 `docs/continuation/startup-checklist.md` 와 `docs/continuation/current-status.md` 를 읽는다.
- 이 순서를 건너뛰고 바로 코드부터 보지 않는다.
- 저장소 상태를 복원해야 하는 세션이면 `startup-checklist.md` 의 환경 확인 절차까지 함께 따른다.

### Before Changing Code

- 먼저 관련 문서를 읽는다.
- 새 세션이거나 다른 환경에서 이어받은 작업이면 `docs/continuation/startup-checklist.md` 와 `docs/continuation/current-status.md` 를 먼저 읽는다.
- 해당 작업이 MVP 범위인지 확인한다.
- 데이터 구조를 바꾸는 작업이면 `docs/data/` 와 `docs/operations/` 부터 확인한다.
- 화면 구조를 바꾸는 작업이면 `docs/product/` 를 먼저 확인한다.

### Before Changing Docs

- 같은 주제를 다루는 문서가 이미 있는지 확인한다.
- 확정 사항과 가정 사항을 섞지 않는다.
- 선수, 팀, 경기의 조회 단위를 혼동하지 않는다.

### Before Designing Scrapers

- KBO 공식 홈페이지를 기본 원천 데이터 소스로 본다.
- `SCRAPLING` 을 기본 후보로 두되, 페이지별로 정적 fetch 와 동적 fetch 필요성을 구분한다.
- 경기 상세는 raw 이벤트 보존이 목표이므로 요약 정보만 저장하는 설계를 피한다.

## Domain Rules

- 선수 페이지는 커리어 기준의 시즌별 기록이 핵심이다.
- 팀 페이지는 팀의 시즌별 누적 기록이 핵심이다.
- 경기 페이지는 raw 경기 흐름과 회차별 점수, 이벤트 로그가 핵심이다.
- 고급 지표는 기본 기록이 충분히 확보된 뒤 계산한다.
- `wRC+`, `OPS+`, `ERA+`, `FIP`, `xFIP` 는 리그 평균, 보정치, 상수 데이터 없이는 완전하지 않다.

## Task Routing

### Product / Screen Questions

- 먼저 `docs/product/service-overview.md`
- 다음 `docs/product/information-architecture.md`

### Data Modeling Questions

- 먼저 `docs/data/domain-model.md`
- 다음 `docs/data/statistics-catalog.md`
- 고급 지표면 `docs/data/advanced-metric-dependencies.md`

### Scraping / Pipeline Questions

- 먼저 `docs/operations/data-pipeline.md`
- 다음 `docs/operations/kbo-source-inventory.md`

### Repo Process / Commit Questions

- `RULES.md` 를 기준으로 따른다.

## AI-Specific Behavior

- 저장소 문서를 읽지 않고 도메인 결정을 단정하지 않는다.
- 같은 내용을 `RULES.md` 와 `AGENTS.md` 에 중복 복사하지 않는다.
- AI 역할 정의는 가능하지만, 강한 캐릭터성보다 저장소 맥락과 우선순위를 제공하는 데 집중한다.
- 구현보다 앞서 문서가 필요한 작업이면 문서부터 갱신한다.
- 스크래핑 관련 변경은 원천 페이지, 식별자, 중복 방지, 실패 처리까지 함께 검토한다.
- 의미 있는 작업이 끝나면 `docs/continuation/current-status.md` 를 함께 갱신해 다음 세션이 바로 이어질 수 있게 한다.
- 다른 컴퓨터에서 이어받을 가능성이 있으면 `current-status.md` 만이 아니라 `startup-checklist.md` 기준으로 환경 복원 정보도 함께 유지한다.

## Common Pitfalls

- 선수 시즌 기록과 경기 기록을 한 테이블 개념으로 단순화하는 것
- 팀 페이지를 경기 상세 화면처럼 설계하는 것
- 공식 페이지에서 제공하는 raw 이벤트를 요약 정보로만 축소하는 것
- 고급 지표를 리그 기준 데이터 없이 바로 확정값처럼 노출하는 것
- 문서 변경 없이 구조를 먼저 구현하는 것

## Next Useful Reads

- `RULES.md`
- `docs/continuation/startup-checklist.md`
- `docs/continuation/current-status.md`
- `docs/README.md`
- `docs/product/service-overview.md`
- `docs/data/domain-model.md`
- `docs/operations/kbo-source-inventory.md`
