# KBO Source Inventory

## Goal

KBO 공식 홈페이지에서 어떤 페이지와 데이터 조합을 우선 수집해야 하는지 정리한다. 이 문서는 스크래핑 구현 전에 대상 페이지를 빠르게 파악하고, 어느 데이터가 MVP에 직접 연결되는지 구분하기 위한 기준 문서다.

## Primary Source Policy

- 기본 원천 데이터 소스는 KBO 공식 홈페이지로 한다.
- 스크래핑 라이브러리 기본 후보는 Python `SCRAPLING` 으로 둔다.
- 초기 구현은 가능한 한 공식 페이지의 구조와 필드를 그대로 보존하되, 내부 저장 시 표준화된 스키마로 정제한다.

## Verified KBO Entry Points

직접 확인한 공식 사이트 진입점은 다음과 같다.

- 일정/결과: `/Schedule/Schedule.aspx`
- 스코어보드: `/Schedule/ScoreBoard.aspx`
- 게임센터: `/Schedule/GameCenter/Main.aspx`
- 기록실(선수 타자 기본): `/Record/Player/HitterBasic/Basic1.aspx`
- 기록실(팀 타격 기본): `/Record/Team/Hitter/Basic1.aspx`
- 팀 순위: `/Record/TeamRank/TeamRank.aspx`
- 팀 순위(일자별): `/Record/TeamRank/TeamRankDaily.aspx`
- 선수 순위: `/Record/Ranking/Top5.aspx`
- 선수 조회: `/Player/Search.aspx`
- 선수 이동 현황: `/Player/Trade.aspx`
- 구단 소개: `/Kbo/League/TeamInfo.aspx`
- 구단 변천사: `/Kbo/League/TeamHistory.aspx`

이 구조는 일정, 팀, 선수, 참고 정보가 서로 별도 페이지로 나뉘어 있어 페이지 유형별 스크래퍼를 분리하기에 적합하다.

## Page Categories To Inventory First

### Daily Game and Schedule Pages

- 일별 경기 일정 페이지
- 일별 스코어보드 페이지
- 경기 상태(예정, 종료, 취소, 연기) 확인 페이지

이 영역은 경기 목록 진입점과 일일 수집 기준점을 제공한다. 시즌 진행 중 하루 1회 업데이트 파이프라인의 시작 지점이 된다.

실제 확인 결과 `경기일정・결과` 페이지는 날짜, 시간, 경기, 게임센터 링크, 하이라이트 링크, TV, 라디오, 구장, 비고 필드를 포함한다.

### Game Detail Pages

- 박스 스코어
- 경기 상세 기록
- 회차별 점수표
- 주요 이벤트 또는 문자 중계성 이벤트 흐름

이 영역은 raw 경기 데이터 수집의 핵심이다. 경기 상세 화면에서 최종 스코어, 회차별 점수, 선수별 경기 기록, 타석/교체/득점 이벤트를 재구성할 수 있어야 한다.

실제 확인 결과 `스코어보드` 페이지는 날짜별 경기 목록, 경기 종료 상태, 승/패/세이브 투수, 구장, 시작 시각, 문자중계 버튼, 리뷰 버튼, 회차별 점수표, R/H/E/B 집계까지 제공한다. 리뷰 링크는 `gameDate` 와 `gameId` 파라미터를 포함하므로 경기 식별자 수집의 기준점으로 활용할 수 있다.

직접 확인한 링크 형식은 `/Schedule/GameCenter/Main.aspx?gameDate=YYYYMMDD&gameId={gameId}&section=REVIEW` 이다. 따라서 `ScoreBoard` 만으로도 날짜와 경기 식별자, 기본 리뷰 진입 URL 패턴을 안정적으로 확보할 수 있다.

반면 `게임센터` 메인 페이지는 정적 fetch 시 경기 상세 자체보다 shell 구조와 초기 스크립트가 중심으로 내려오며, 날짜와 경기 목록은 `/ws/Main.asmx/GetKboGameDate`, `/ws/Main.asmx/GetKboGameList` 호출을 통해 채워진다. 즉 게임센터는 정적 HTML만 읽는 방식보다 스크립트가 호출하는 보조 요청까지 함께 추적하는 접근이 필요하다.

직접 확인한 inline script 기준으로 `게임센터` 탭 상세는 `S2iAjaxHtml` 를 통해 별도 HTML 조각을 불러온다. 현재 확인된 경로는 다음과 같다.

- `/Schedule/GameCenter/Preview/StartPitcher.aspx`
- `/Schedule/GameCenter/Preview/Team.aspx`
- `/Schedule/GameCenter/Preview/LineUp.aspx`
- `/Schedule/GameCenter/ReviewNew.aspx`
- `/Schedule/GameCenter/KeyPlayerPitcher.aspx?version=20181219`
- `/Schedule/GameCenter/KeyPlayerHitter.aspx?version=20181219`
- `/Schedule/GameCenter/Highlight.aspx`

이로써 게임센터 상세는 단일 JSON API보다는 `ws/Main.asmx` 기반 메타데이터 조회 + section별 HTML partial 로딩 구조에 가깝다는 점까지는 확인되었다. 다만 실제 play-by-play 수준의 raw 이벤트가 어떤 경로로 제공되는지는 아직 확정하지 못했다.

### Player Statistics Pages

- 타자 시즌 기록 페이지
- 투수 시즌 기록 페이지
- 선수 검색 또는 선수 상세 페이지
- 선수 커리어 기록 페이지

이 영역은 선수 화면의 데뷔 이후 시즌별 기록과 프로필 정보 수집에 사용한다.

실제 확인 결과 `선수 조회` 페이지는 팀, 포지션 기반 필터와 등번호, 선수명, 팀명, 포지션, 생년월일, 체격, 출신교 필드를 제공한다.

추가 확인 결과 `선수 조회` 는 `/ws/Controls.asmx/GetSearchPlayer` 호출을 사용하며, 응답의 `P_LINK` 를 통해 선수 상세 페이지로 이동한다. 현재 확인된 링크 패턴은 다음과 같다.

- 현역 타자 예시: `/Record/Player/HitterDetail/Basic.aspx?playerId=62404`
- 은퇴 타자 예시: `/Record/Retire/Hitter.aspx?playerId=67341`

즉 선수 상세 페이지는 `Player/Search.aspx` 와 별개로 `Record/Player/*Detail/*` 또는 `Record/Retire/*` 경로 아래에 존재한다.

현역 선수 상세 페이지에서는 팀, 프로필 이미지, 선수명, 등번호, 생년월일, 포지션/타투유형, 신장/체중, 경력, 지명순위, 입단년도와 함께 다음 탭 구조를 확인했다.

- `Basic.aspx`
- `Total.aspx`
- `Daily.aspx`
- `Game.aspx`
- `Situation.aspx`
- `Award.aspx`
- `SeasonReg.aspx`

은퇴 선수 페이지는 현역 상세보다 간소한 프로필과 연도별 통산 기록 중심 구성을 제공한다.

실제 확인 결과 `기록실` 은 2002년부터 최근 시즌까지 연도 기준 조회를 제공하고, 정규시즌/시범경기/포스트시즌 구분과 월별, 구장별, 홈/방문, 상대팀별, 주/야간별, 주자상황별, 볼카운트별, 아웃카운트별, 이닝별, 타순별 같은 세부 필터를 제공한다.

### Team Statistics Pages

- 팀 시즌 기록 페이지
- 팀 순위 페이지
- 팀별 타격 기록 페이지
- 팀별 투수 기록 페이지

이 영역은 팀 상세 화면에서 시즌별 누적 기록과 시즌 흐름을 제공하는 기반이 된다.

실제 확인 결과 `팀 순위` 연도별 페이지는 순위, 경기, 승/패/무, 승률, 게임차, 최근 10경기, 연속, 홈/방문 성적과 팀간 승패표를 제공한다.

### Reference Pages

- 팀 정보 페이지
- 구장 정보 페이지
- 로스터 또는 선수단 페이지

이 영역은 팀명 표준화, 홈 구장 정보, 선수 소속 정보 정리에 사용한다.

실제 확인 결과 `선수 이동 현황` 페이지가 별도 존재하며, 날짜, 항목, 팀, 선수, 비고 필드를 제공한다. 따라서 공식 원천 데이터만으로도 트레이드, FA 계약, 등록/말소 성격의 이동 이벤트 이력은 일정 수준까지 확보할 수 있다.

## MVP Mapping

### High Priority

- 일별 경기 일정 및 스코어보드
- 경기 상세 및 박스 스코어
- 선수 시즌 기록 페이지
- 팀 시즌 기록 및 순위 페이지
- 선수 검색 또는 선수 상세 페이지

### Medium Priority

- 팀 정보 및 로스터 페이지
- 구장 정보 페이지
- 팀별 세부 타격/투수 집계 페이지

### Later Priority

- Top5/리더보드 변형 페이지
- 부가 통계 요약 페이지
- 시각화 전용 페이지

## Field Checklist By Page Type

### Schedule / Scoreboard

- 경기 날짜
- 경기 식별자
- 홈 팀 / 원정 팀
- 경기 시작 시각
- 경기 상태
- 최종 점수
- 회차별 점수
- R/H/E/B 집계
- 승/패/세이브 투수
- 리뷰 링크의 `gameDate`, `gameId`

### Game Detail

- 회차별 점수
- 선발 라인업
- 선수별 타격 기록
- 선수별 투수 기록
- 교체 정보
- 득점 장면
- 타석 결과 또는 이벤트 로그

### Player Page

- 선수명
- 팀
- 포지션
- 생년월일
- 등번호
- 시즌별 기록
- 커리어 기록
- 이적 또는 소속 이력
- 체격
- 출신교

### Team Page

- 시즌
- 팀명
- 승/패/무
- 승률
- 순위
- 팀 타격 지표
- 팀 투수 지표
- 최근 10경기
- 연속 기록
- 홈/방문 성적
- 팀간 승패표

## SCRAPLING Usage Notes

- 초기에는 단순 fetch 기반으로 정적 페이지 접근 가능 여부를 확인한다.
- JavaScript 렌더링이나 동적 로딩이 필요한 경우 `SCRAPLING` 의 동적 fetch 전략을 검토한다.
- 페이지 구조 변경 가능성이 있으므로 selector는 페이지 유형별로 관리한다.
- 수집 대상 페이지별로 rate limit, 재시도, 실패 로깅 정책을 분리한다.
- `Schedule/ScoreBoard.aspx` 처럼 정적 HTML에서 핵심 필드가 보이는 페이지와 `GameCenter/Main.aspx` 처럼 동적 접근 가능성이 높은 페이지를 분리해 설계한다.
- `GameCenter/Main.aspx` 는 메타데이터를 `ws/Main.asmx` 로 받고, 상세는 section별 HTML partial 로드가 섞여 있으므로 JSON endpoint만 찾는 방식으로 단순화하지 않는다.
- `Player/Search.aspx` 는 검색 목록 자체와 상세 진입 링크를 함께 제공하므로, 선수 식별자 확보 단계와 상세 수집 단계를 분리해서 설계한다.
- KBO 공식 사이트는 ASP.NET `__doPostBack` 기반 네비게이션이 섞여 있으므로, 페이지 전환/정렬/페이징 수집에서는 단순 링크 파싱만으로 충분하지 않을 수 있다.
- 현재 확인된 범위에서는 공식 API가 보이지 않으므로, 기본 전략은 HTML 스크래핑이다.

## Open Questions

- KBO 공식 홈페이지에서 play-by-play 수준의 raw 이벤트 로그를 어떤 요청 구조로 제공하는가?
- 현역 투수 상세와 은퇴 투수 상세가 타자 상세와 동일한 수준의 필드/탭 구조를 안정적으로 제공하는가?
- 고급 지표 계산에 필요한 리그 평균과 구장 보정 데이터를 공식 페이지만으로 확보할 수 있는가?
- robots.txt 와 실제 요청 제한 정책 기준에서 어떤 페이지군까지 안정적으로 배치 수집 가능한가?

## MVP Decision Gates

- 선수 이동 이력은 `선수 이동 현황` 페이지 기준으로 우선 확보하고, 커리어 전체 이력 완성도가 부족하면 MVP에서는 이동 이벤트 중심으로 제공한다.
- 리그 평균 또는 구장 보정 데이터가 부족하면, Tier 2 이상 고급 지표는 MVP 전면 제공 대상에서 제외하고 단계적 공개로 전환한다.
- 게임센터 이벤트 로그 접근이 제한적이면, 경기 상세 화면은 회차별 점수와 박스 스코어 중심으로 먼저 출시한다.
