# Statistics Catalog

## Player Statistics

선수 상세 화면은 한 선수의 데뷔 시즌부터 현재까지 이어지는 시즌별 기록을 기본으로 제공한다. 화면은 타자와 투수를 구분해 각 역할에 맞는 지표를 보여줄 수 있어야 하며, 동일 선수의 커리어 흐름을 연도별로 비교하기 쉬운 구조를 가져야 한다.

### Player Profile

- 선수명
- 현재 소속 팀
- 포지션
- 생년월일
- 나이 또는 만 나이 기준 정보
- 등번호
- 데뷔 시즌
- 소속 팀 이력 및 이적 이력

### Hitter Basic Statistics

- 경기 수
- 타석
- 타수
- 득점
- 안타
- 2루타
- 3루타
- 홈런
- 타점
- 볼넷
- 고의사구
- 삼진
- 사구
- 희생번트
- 희생플라이
- 도루
- 도루 실패
- 병살타
- AVG
- OBP
- SLG
- OPS

### Hitter Advanced Statistics

- ISO
- BABIP
- BB%
- K%
- wOBA
- wRC
- wRC+
- OPS+
- WAR

### Pitcher Basic Statistics

- 경기 수
- 선발 경기 수
- 이닝
- 승
- 패
- 세이브
- 홀드
- 평균자책점
- 피안타
- 피홈런
- 볼넷
- 사구
- 탈삼진
- 실점
- 자책점
- WHIP
- K/9
- BB/9
- K/BB

### Pitcher Advanced Statistics

- FIP
- xFIP
- ERA+
- FIP-
- BABIP allowed
- LOB%
- HR/FB
- WAR

## Team Statistics

팀 화면은 특정 팀이 시즌별로 어떤 기록을 쌓아왔는지 확인하는 화면이다. 사용자는 시즌을 선택한 뒤, 해당 시즌의 팀 성적과 팀 타격/투수 누적 지표를 확인할 수 있어야 한다.

### Team Season Summary

- 시즌
- 팀명
- 경기 수
- 승/패/무
- 승률
- 순위
- 득점
- 실점
- 득실차

### Team Season Statistics

- 경기 수
- 승/패/무
- 승률
- 팀 득점
- 팀 실점
- 팀 타율
- 팀 출루율
- 팀 장타율
- 팀 OPS
- 팀 홈런
- 팀 도루
- 팀 평균자책점
- 팀 WHIP

### Team Season Flow

- 시즌 누적 성적 변화
- 월별 또는 시점별 성적 흐름
- 시즌 내 주요 경기 결과 연결

고급 팀 지표는 선수 및 경기 데이터 정합성이 확보된 후 단계적으로 확대한다.

## Game-Level Statistics

경기 상세 화면은 우리가 스크래핑하는 가장 raw한 형태의 경기 데이터를 사용자에게 보여주는 화면이다. 단순 요약보다 원본 경기 흐름을 재구성할 수 있는 정보 제공이 목표다.

### Game Summary

- 경기 일시
- 홈/원정 팀
- 최종 스코어
- 경기 상태
- 선발 투수 정보

### Inning-by-Inning Data

- 회차별 득점
- 회차별 누적 스코어
- 각 회차 주요 이벤트

### Player-Level Game Records

- 주요 타자 기록
- 주요 투수 기록
- 팀 타격 요약
- 팀 투구 요약

### Raw Event Data

- 타석 결과
- 득점 장면
- 주자 진루 상황
- 투수 교체
- 수비 결과
- 어떤 선수가 어떤 회차에서 어떤 플레이를 했는지 추적 가능한 이벤트 로그

## Derived Metrics

초기 서비스는 기본 기록 제공이 우선이지만, 가능하다면 사이버메트릭 지표까지 함께 제공하는 것을 목표로 한다. 고급 지표는 원천 데이터만으로 계산 가능한지, 리그 평균이나 파크 팩터 같은 추가 기준값이 필요한지에 따라 구현 난도가 달라진다.

- 즉시 도입 우선 후보: OPS, OBP, SLG, WHIP, K/BB, K/9, BB/9
- 추가 계산 규칙 검토 필요: wOBA, wRC, wRC+, OPS+, FIP, xFIP, ERA+
- 추가 기준 데이터 필요 가능성: 리그 평균, 시즌 평균, 구장 보정치, 대체 수준 기준값
- 향후 예측 확장 후보: 최근 N경기 폼, 월별 추세, 상대 전적 기반 파생 지표
