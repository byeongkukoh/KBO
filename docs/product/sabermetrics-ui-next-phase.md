# Sabermetrics UI Next Phase

## Purpose

현재 시즌 센터와 선수/팀 상세 UI가 사베르메트릭스 중심 탐색에 어느 정도 적합한지 평가하고, 다음 단계 구현 작업을 성격별로 분리한다.

## Verdict

현재 UI는 사베르메트릭스 입문과 중간 수준 탐색에는 usable한 기반이지만, 진지한 비교/해석 워크플로를 지원하는 sabermetrics-grade UI로 보기에는 아직 부족하다.

그 이유는 다음 두 축이 동시에 존재하기 때문이다.

- 이미 제공되는 값은 충분히 의미 있다. 시즌 센터 전체 기록표와 선수 상세는 `ISO`, `BABIP`, `BB%`, `K%`, `wOBA`, `wRC`, `wRC+`, `WHIP`, `K/9`, `BB/9`, `K/BB`, `FIP`, 팀 상세의 `OPS+`, `ERA+` 까지 노출한다.
- 하지만 사용자가 그 값을 해석하고 비교하는 데 필요한 맥락 장치가 부족하다. 현재 UI에는 지표 설명, 리그 평균 대비 위치, 표본 기준, split 비교, 커스텀 dense table 제어, 연도 간 변화 강조가 약하다.

즉 지금 상태는 "지표를 보여주는 UI" 에는 도달했지만, "지표를 읽고 판단하게 해주는 UI" 로는 아직 한 단계가 남아 있다.

## What Already Works Well

- 시즌 센터 전체 기록표가 기본 기록과 고급 지표를 한 화면에 함께 보여준다.
- 선수 상세가 metric card, 월별 추이, 커리어 시즌 요약, 경기 로그를 연결해 탐색 흐름을 만든다.
- 선수 비교가 월별 line chart 와 2인 비교 진입점을 제공한다.
- 팀 상세가 `OPS+`, `ERA+`, 최근 경기 흐름을 함께 제공해 팀 단위 분석의 시작점을 만든다.
- freshness 메타데이터와 snapshot label 이 있어 데이터 최신성/적재 시점을 노출할 수 있다.
- qualified hitter / pitcher 토글이 이미 있어 규정 기록 기준의 첫 단계는 들어와 있다.

## Current Gaps For Sabermetrics Use

### 1. Metric Explainability Is Weak

- `wOBA`, `wRC+`, `FIP`, `OPS+`, `ERA+` 가 보이지만 현재 화면에서 정의, 계산 맥락, 해석 방향을 바로 알기 어렵다.
- `docs/data/advanced-metric-dependencies.md` 기준으로 Tier 2 이상 지표는 리그 기준값과 상수에 의존하는데, UI는 이 값이 provisional 인지 충분히 강조하지 못한다.

### 2. Baseline Context Is Missing

- 현재 값은 raw number 중심이라 리그 평균 대비 얼마나 좋은지 빠르게 읽기 어렵다.
- public sabermetrics products 는 percentile, league average, qualifier line, plus-stat baseline(100) 같은 컨텍스트를 함께 준다.

### 3. Comparison UX Is Not Yet Analyst-Friendly

- 현재 선수 비교는 radar + monthly line chart 중심이다.
- radar chart 는 "대략적인 모양" 을 보기는 쉽지만 정확한 수치 읽기, 리그 평균과의 거리, 시즌 간 delta 확인에는 약하다.
- side-by-side stat table, delta view, category preset 같은 보조 비교 장치가 필요하다.

### 4. Dense Table Control Is Limited

- 현재 전체 기록표는 wide table 이지만 column show/hide, freeze, preset, 사용자 정의 정렬 묶음이 없다.
- 모바일에서는 고급 지표가 많아질수록 탐색 피로도가 더 커질 가능성이 높다.

### 5. Split Workflow Is Thin

- 월별 추이는 제공되지만, 사베르메트릭스 사용자가 자주 보는 split 축인 홈/원정, 좌/우투수 상대, 전/후반기, 득점권, 구장별 흐름은 아직 없다.
- 팀 상세와 경기 상세도 sabermetrics 관점 drilldown 이 부족하다.

### 6. Data Trust Cues Need To Be Stronger

- freshness 는 노출되지만 metric-level caveat 이 약하다.
- 특히 `Sidebar` 문구는 아직 "실제 2025 시즌 snapshot" 중심으로 서술되어 있어 현재 멀티 시즌 상태와 완전히 일치하지 않는다.

## Next-Phase Work Split

### Track A. Metric Glossary And Methodology

목표: 사용자가 고급 지표를 "무슨 뜻인지" 와 "어느 정도 신뢰해야 하는지" 바로 이해하게 만든다.

- 지표명 tooltip / glossary 패널 추가
- `+` 계열 지표의 기준선(100) 명시
- Tier 2 지표에 provisional baseline/constant 사용 여부 표시
- 시즌/시리즈별 계산 기준과 source note 연결

### Track B. Baseline And Qualification Framing

목표: 숫자를 단독 값이 아니라 해석 가능한 비교 값으로 전환한다.

- 규정 타석/규정 이닝 기준을 더 명시적으로 노출
- leaderboard 와 player detail 에 qualifier 상태 배지 강화
- league average / percentile / plus-stat baseline 시각화 검토
- small sample 경고 또는 최소 표본 가이드 추가

### Track C. Comparison Workflow Upgrade

목표: 비교를 "그림" 이 아니라 "판단 가능한 분석 화면" 으로 바꾼다.

- 선수 비교에 side-by-side stat table 추가
- absolute value 와 delta 를 함께 보여주는 비교 모드 추가
- radar 중심 구조를 보조할 table/bar 기반 비교 패턴 보강
- 자주 쓰는 비교 preset(타격 생산, 출루/삼진, pitching dominance 등) 도입 검토

### Track D. Dense Table Ergonomics

목표: 고급 지표가 늘어나도 전체 기록표가 읽히는 상태를 유지한다.

- column preset(Standard / Advanced / Team Context 등) 추가
- column show/hide 또는 경량 customization 추가
- 첫 열 고정, 모바일 sticky header, 수평 스크롤 UX 점검
- 정렬 기준 전환 시 선택 상태와 설명을 더 명확하게 노출

### Track E. Split Expansion

목표: 월별 추이를 넘어 실제 분석에 쓰는 split 탐색을 확장한다.

- 홈/원정 split
- 좌/우투수 상대 split
- 전반기/후반기 split
- 필요 시 구장별/상대팀별 split

### Track F. Team And Game Analytical Depth

목표: 현재 선수 중심 구조를 팀/경기 단위 분석까지 연결한다.

- 팀 상세에 시즌 누적 고급 지표 묶음 확장
- 팀 비교 진입점 검토
- 경기 상세에 sabermetrics 관점의 핵심 요약 카드 검토
- 장기적으로 raw event 기반 확장 지점과 연결

### Track G. Trust, Freshness, And Source Communication

목표: "왜 이 값을 믿어도 되는지" 를 화면에서 설명한다.

- 화면별 freshness 위치와 표현 통일
- 데이터 source, 마지막 적재, context refresh 시점의 역할 구분
- provisional metric note 를 player/team/leaderboard 화면 전반에 일관되게 반영
- 현재 멀티 시즌 상태와 맞지 않는 설명 문구 정리

## Suggested Delivery Order

1. Track A `Metric Glossary And Methodology`
2. Track B `Baseline And Qualification Framing`
3. Track C `Comparison Workflow Upgrade`
4. Track D `Dense Table Ergonomics`
5. Track E `Split Expansion`
6. Track F `Team And Game Analytical Depth`
7. Track G `Trust, Freshness, And Source Communication`

이 순서를 권장하는 이유는, 먼저 지표 해석과 신뢰성 문제를 풀어야 이후의 비교/확장 UI가 의미를 갖기 때문이다.

## Non-Goals For The Immediate Next Step

- WAR, xFIP, park-adjusted metrics 같은 Tier 3 확장을 바로 UI 메인에 올리지 않는다.
- 커스텀 리더보드 저장, 개인화, 계정 기능은 후순위로 둔다.
- 실시간 경기 중계 수준의 in-game analytical UI 는 현재 단계에서 다루지 않는다.

## Acceptance Criteria For A Stronger Sabermetrics UI

- 사용자가 `wRC+`, `FIP`, `OPS+`, `ERA+` 를 화면 내에서 바로 해석할 수 있다.
- leaderboards 와 detail 화면에서 qualifier 와 provisional 상태를 오해 없이 읽을 수 있다.
- 두 선수 비교 시 raw value, delta, 월별 흐름을 함께 볼 수 있다.
- 전체 기록표가 모바일과 데스크톱 모두에서 읽을 만한 밀도를 유지한다.
- 팀/선수/경기 화면 모두에서 freshness 와 source trust 문구가 일관된다.

## External Product Patterns Referenced

- FanGraphs: dense leaderboard control, glossary, qualification/split workflow
- Baseball Savant: percentile/baseline framing, comparison workflow, metric context
- Nielsen Norman Group mobile table guidance: dense table mobile ergonomics
