# System Overview

## Repository Layout

- `apps/web`: 사용자에게 기록 조회 화면을 제공하는 React 기반 프론트엔드
- `apps/api`: 기록 조회 API와 향후 데이터 연동 로직을 제공하는 FastAPI 백엔드
- `docs/`: 서비스 기획, 데이터 설계, 운영 문서를 관리하는 디렉토리

현재는 웹과 API 두 프로젝트로 시작하지만, 이후 스크래퍼, 배치 워커, 예측 모델 프로젝트가 추가될 수 있는 monorepo 구조를 유지한다.

## Application Boundaries

- Frontend는 사용자 탐색 경험과 화면 렌더링을 담당한다.
- API는 시즌 기록, 팀 기록, 선수 기록, 경기 기록 조회를 위한 데이터 제공 계층을 담당한다.
- API는 선수 프로필, 팀 이력, 시즌별 커리어 기록, 고급 지표 응답을 함께 제공할 수 있어야 한다.
- MVP 단계에서는 KBO 원천 수집, 정제, 적재를 하나의 ingestion 앱 경계에서 먼저 구현하고, 책임은 내부 모듈 수준에서 source collection 과 batch orchestration 으로 나눈다.
- 향후 Scraper/Worker는 외부 소스 수집과 배치 처리 책임을 분리해 독립 프로젝트로 추가할 수 있다.
- 예측 모델 기능은 MVP 범위 밖이므로 추후 별도 서비스 또는 별도 모듈로 확장할 수 있다.

## External Dependencies

- 외부 기록 제공 웹 소스: 선수 기록, 팀 기록, 경기 기록 수집 대상
- PostgreSQL: 서비스의 주 저장소로 사용할 예정인 관계형 데이터베이스
- 스케줄링 환경: 하루 1회 수집 작업을 실행하기 위한 배치 실행 환경

## Future Extension Points

- MVP 우선 방향: 단일 ingestion 앱(`apps/worker` 또는 `apps/scraper`)에서 스크래핑과 일일 적재를 함께 수행
- 확장 방향: 필요 시 `apps/scraper` 와 `apps/worker` 로 분리해 source fetching 과 orchestration 책임을 나눈다.
- `packages/shared` 같은 공통 모듈: 타입, 유틸리티, 공통 스키마 공유
- 예측 모델 파이프라인: 축적된 기록 데이터를 활용한 순위 예측 기능
- 운영 모니터링 영역: 수집 성공 여부, 데이터 최신성, 오류 알림 체계
