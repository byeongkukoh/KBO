# KBO Record

KBO 선수 기록과 팀 기록을 시즌별, 경기별로 조회할 수 있는 서비스를 만들기 위한 monorepo 초기 구조입니다.

## Repository Structure

- `apps/web`: React + TypeScript + Tailwind CSS 기반 프론트엔드
- `apps/api`: Conda 기반 Python + FastAPI 백엔드

## Why a monorepo?

프론트엔드와 백엔드를 하나의 Git 저장소에서 함께 관리하면 공통 문서, 도메인 규칙, 일정, 이슈 맥락을 한곳에서 다룰 수 있습니다. 이후 스크래퍼, 배치 작업, 예측 모델, 공통 패키지 같은 프로젝트를 추가하기도 쉬워집니다.

## Frontend

Node.js가 설치된 환경에서 아래 명령으로 시작할 수 있습니다.

```bash
cd apps/web
npm install
npm run dev
```

권장 버전: Node.js 22 LTS 이상

## Backend

Conda 환경 생성 및 실행:

```bash
conda env create -f apps/api/environment.yml
conda activate kbo-record-api
pip install -e ./apps/api[dev]
uvicorn app.main:app --reload --app-dir apps/api
```

권장 Python 버전은 3.12 계열로 설정했습니다. 최신 안정 흐름을 따르면서도 FastAPI 생태계와의 호환성과 패키지 안정성을 우선한 선택입니다.

## Current Scope

- 초기 monorepo 구조 생성
- 웹 앱과 API 서버 시작점 구성
- 추후 PostgreSQL 연결, 스크래핑 파이프라인, 배치 업데이트, 순위 예측 기능 확장 예정
