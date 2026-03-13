# Advanced Metric Dependencies

## Goal

사이버메트릭 지표를 계산하기 위해 어떤 원천 기록과 추가 기준 데이터가 필요한지 정리한다. 이 문서는 구현 우선순위를 정하고, 어떤 지표가 즉시 계산 가능한지와 추가 데이터 수집이 필요한 지표를 구분하기 위한 문서다.

## Metric Tiers

### Tier 1: Immediate Metrics

원천 기록만으로 비교적 쉽게 계산 가능하거나 이미 기본 기록에서 직접 파생 가능한 지표다.

- AVG
- OBP
- SLG
- OPS
- WHIP
- K/9
- BB/9
- K/BB

### Tier 2: Advanced Metrics With Formula Dependencies

원천 기록 외에도 시즌 기준값이나 리그 평균이 필요한 지표다.

- wOBA
- wRC
- wRC+
- OPS+
- ERA+
- FIP
- xFIP

### Tier 3: Advanced Metrics With Contextual Dependencies

구장 보정치, 대체 수준, 리그 환경 차이 같은 추가 맥락 데이터가 필요한 지표다.

- WAR
- park-adjusted batting metrics
- park-adjusted pitching metrics

## Required Raw Inputs

### Hitter Inputs

- PA
- AB
- H
- 2B
- 3B
- HR
- BB
- IBB
- HBP
- SO
- SF
- SH
- SB
- CS

### Pitcher Inputs

- IP
- H
- HR
- BB
- HBP
- SO
- ER
- BF or opponent batters faced if available
- FB or batted-ball splits if xFIP level 계산을 목표로 한다면 필요 가능

## League Baseline Datasets

### Batting Context

- 시즌별 리그 평균 OBP
- 시즌별 리그 평균 SLG
- 시즌별 리그 평균 OPS
- 시즌별 리그 전체 득점
- 시즌별 리그 전체 PA, AB, H, BB, HBP, SF

이 데이터는 OPS+, wOBA, wRC, wRC+ 계산에 기본적으로 필요하다.

### Pitching Context

- 시즌별 리그 평균 ERA
- 시즌별 리그 평균 FIP 계산용 HR, BB, HBP, SO 비율
- 시즌별 리그 평균 HR/FB

이 데이터는 ERA+, FIP, xFIP 계산에 필요하다.

## Park Factor Datasets

- 구장별 득점 환경 보정치
- 구장별 홈런 보정치
- 필요 시 BABIP 또는 장타 관련 보정치

구장 보정치는 KBO 구장별 특성을 반영하기 위해 중요하다. OPS+, ERA+, WAR 계열 지표의 품질에 직접 영향을 준다.

## Weight Constants

### wOBA / wRC Family

- 단타, 2루타, 3루타, 홈런, 볼넷, 사구에 대한 리그별 weight
- 시즌별 wOBA baseline
- wRC 변환 상수

이 값은 MLB 기준을 그대로 쓰기보다 KBO 시즌 데이터를 바탕으로 별도 검토하는 것이 바람직하다.

### FIP / xFIP Family

- 시즌별 FIP constant
- 시즌별 리그 평균 HR/FB

## Data Acquisition Strategy

### Collect Directly From KBO Source If Possible

- 시즌별 선수 기본 기록
- 시즌별 팀 기본 기록
- 경기별 raw 기록
- 시즌별 리그 전체 집계에 필요한 기본 분모 데이터

### Derive Internally

- OPS
- WHIP
- K/9
- BB/9
- K/BB
- 필요 조건이 충족된 이후의 wOBA, wRC, wRC+, OPS+, ERA+, FIP, xFIP

### May Require Additional Research Or Secondary Inputs

- 구장 보정치
- 리그별 weight constant
- WAR 계산 기준
- 대체 수준 기준값

## Recommended Rollout

### Phase 1

- 기본 기록과 Tier 1 지표 제공

### Phase 2

- 리그 평균 데이터 확보 후 wOBA, wRC, wRC+, OPS+, ERA+, FIP 도입 검토

### Phase 3

- 구장 보정치와 추가 기준값 확보 후 xFIP, WAR, park-adjusted 지표 확장

## Open Questions

- KBO 공식 소스에서 리그 전체 집계 데이터를 직접 제공하는가?
- KBO 기준 park factor를 직접 계산할 수 있을 정도의 홈/원정 분리 데이터가 확보되는가?
- KBO 전용 wOBA weight와 FIP constant를 내부 계산으로 둘지, 검증된 외부 기준을 참고할지 결정해야 한다.
