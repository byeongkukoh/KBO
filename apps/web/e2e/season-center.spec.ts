import { expect, test } from "@playwright/test";

const freshness = {
  latest_game_date: "2025-10-04",
  last_successful_sync_at: "2026-03-15T15:00:00+09:00",
  context_updated_at: "2026-03-15T15:05:00+09:00",
};

test("renders db-backed standings and player records", async ({ page }) => {
  await page.route("http://127.0.0.1:8000/api/seasons", async (route) => {
    await route.fulfill({ json: { seasons: [2026, 2025] } });
  });

  await page.route("http://127.0.0.1:8000/api/seasons/2025/snapshot?series_code=regular", async (route) => {
    await route.fulfill({
      json: {
        season: 2025,
        snapshot_label: "2025-10-04 regular db snapshot",
        freshness,
        standings: [
          {
            rank: 1,
            games: 141,
            team_code: "LG",
            team_name: "LG 트윈스",
            wins: 85,
            losses: 56,
            draws: 0,
            win_pct: 0.603,
            games_back: 0,
            runs_scored: 780,
            runs_allowed: 620,
            run_diff: 160,
            hits: 1234,
            doubles: 240,
            batting_avg: 0.281,
            obp: 0.351,
            slg: 0.429,
            ops: 0.78,
            home_runs: 134,
            stolen_bases: 87,
            era: 3.62,
            whip: 1.27,
            last_ten: "7-3",
            streak: "W2",
          },
          {
            rank: 2,
            games: 141,
            team_code: "SS",
            team_name: "삼성 라이온즈",
            wins: 78,
            losses: 63,
            draws: 0,
            win_pct: 0.553,
            games_back: 7,
            runs_scored: 721,
            runs_allowed: 655,
            run_diff: 66,
            hits: 1160,
            doubles: 211,
            batting_avg: 0.271,
            obp: 0.342,
            slg: 0.411,
            ops: 0.753,
            home_runs: 119,
            stolen_bases: 74,
            era: 4.01,
            whip: 1.34,
            last_ten: "5-5",
            streak: "L1",
          },
        ],
        players: [
          {
            player_id: "lg-홍창기",
            player_name: "홍창기",
            team_code: "LG",
            games: 128,
            plate_appearances: 571,
            innings: null,
            batting_avg: 0.344,
            hits: 167,
            doubles: 26,
            home_runs: 13,
            stolen_bases: 18,
            ops: 0.923,
            era: null,
            strikeouts: null,
            wins: null,
            whip: null,
            qualified_hitter: true,
            qualified_pitcher: false,
          },
          {
            player_id: "nc-김주원",
            player_name: "김주원",
            team_code: "NC",
            games: 132,
            plate_appearances: 540,
            innings: null,
            batting_avg: 0.291,
            hits: 149,
            doubles: 28,
            home_runs: 10,
            stolen_bases: 36,
            ops: 0.812,
            era: null,
            strikeouts: null,
            wins: null,
            whip: null,
            qualified_hitter: true,
            qualified_pitcher: false,
          },
          {
            player_id: "ss-원태인",
            player_name: "원태인",
            team_code: "SS",
            games: 29,
            plate_appearances: null,
            innings: 179.2,
            batting_avg: null,
            hits: null,
            doubles: null,
            home_runs: null,
            stolen_bases: null,
            ops: null,
            era: 2.81,
            strikeouts: 164,
            wins: 14,
            whip: 1.06,
            qualified_hitter: false,
            qualified_pitcher: true,
          },
        ],
      },
    });
  });

  await page.route("http://127.0.0.1:8000/api/seasons/2026/snapshot?series_code=regular", async (route) => {
    await route.fulfill({ status: 404, body: '{"detail":"season not found"}', contentType: "application/json" });
  });

  await page.route("http://127.0.0.1:8000/api/teams/LG/season-detail?season=2025&series_code=regular", async (route) => {
    await route.fulfill({
      json: {
        season: 2025,
        series_code: "regular",
        freshness,
        team_code: "LG",
        team_name: "LG 트윈스",
        wins: 85,
        losses: 56,
        draws: 0,
        win_pct: 0.603,
        runs_scored: 780,
        runs_allowed: 620,
        run_diff: 160,
        hits: 1234,
        doubles: 240,
        stolen_bases: 87,
        batting_avg: 0.281,
        ops: 0.78,
        era: 3.62,
        whip: 1.27,
        ops_plus: 106.2,
        era_plus: 109.4,
        last_ten: "7-3",
        streak: "W2",
        recent_games: [
          {
            game_id: "20251001LGSK0",
            game_date: "2025-10-01",
            series_code: "regular",
            stadium: "잠실",
            result: "W",
            opponent_team_code: "SS",
            team_score: 5,
            opponent_score: 3,
          },
        ],
      },
    });
  });

  await page.route(/http:\/\/127\.0\.0\.1:8000\/api\/games\?.*/, async (route) => {
    await route.fulfill({
      json: {
        season: 2025,
        series_code: "regular",
        team_code: null,
        game_date: null,
        freshness,
        page: 1,
        page_size: 25,
        total_count: 2,
        total_pages: 1,
        items: [
          {
            game_id: "20251001LGSK0",
            game_date: "2025-10-01",
            series_code: "regular",
            series_name: "정규경기",
            stadium: "잠실",
            away_team_code: "SS",
            home_team_code: "LG",
            away_score: 3,
            home_score: 5,
            status_code: "3",
          },
          {
            game_id: "20250930NCWO0",
            game_date: "2025-09-30",
            series_code: "regular",
            series_name: "정규경기",
            stadium: "창원",
            away_team_code: "WO",
            home_team_code: "NC",
            away_score: 1,
            home_score: 2,
            status_code: "3",
          },
        ],
      },
    });
  });

  await page.route("http://127.0.0.1:8000/api/games/20251001LGSK0", async (route) => {
    await route.fulfill({
      json: {
        game_id: "20251001LGSK0",
        game_date: "2025-10-01",
        status_code: "3",
        stadium: "잠실",
        away_team_code: "SS",
        home_team_code: "LG",
        away_score: 3,
        home_score: 5,
        freshness,
        innings: [
          { inning_no: 1, away_runs: 1, home_runs: 0 },
          { inning_no: 2, away_runs: 0, home_runs: 2 },
        ],
        team_stats: [
          { team_code: "SS", team_name: "삼성 라이온즈", runs: 3, hits: 7, errors: 1, walks: 2 },
          { team_code: "LG", team_name: "LG 트윈스", runs: 5, hits: 9, errors: 0, walks: 4 },
        ],
        batting_rows: [],
        pitching_rows: [],
      },
    });
  });

  await page.route(/http:\/\/127\.0\.0\.1:8000\/api\/seasons\/2025\/player-records.*/, async (route) => {
    const url = new URL(route.request().url());
    const group = url.searchParams.get("group");
    if (group === "pitchers") {
      await route.fulfill({
        json: {
          season: 2025,
          series_code: "regular",
          group: "pitchers",
          sort_key: "era",
          qualified_only: true,
          page: 1,
          page_size: 25,
          total_count: 2,
          total_pages: 1,
          snapshot_label: "2025-10-04 regular db snapshot",
          freshness,
          items: [
            {
              rank: 1,
              player_type: "pitcher",
              player_id: "ss-원태인",
              player_name: "원태인",
              team_code: "SS",
              games: 29,
              plate_appearances: null,
              innings: 179.2,
              innings_display: "179.2",
              innings_outs: 539,
              batting_avg: null,
              hits: null,
              doubles: null,
              home_runs: null,
              stolen_bases: null,
              ops: null,
              era: 2.81,
              strikeouts: 164,
              wins: 14,
              whip: 1.06,
              qualified_hitter: false,
              qualified_pitcher: true,
            },
            {
              rank: 2,
              player_type: "pitcher",
              player_id: "lg-엔스",
              player_name: "엔스",
              team_code: "LG",
              games: 28,
              plate_appearances: null,
              innings: 171.1,
              innings_display: "171.1",
              innings_outs: 514,
              batting_avg: null,
              hits: null,
              doubles: null,
              home_runs: null,
              stolen_bases: null,
              ops: null,
              era: 3.18,
              strikeouts: 155,
              wins: 13,
              whip: 1.12,
              qualified_hitter: false,
              qualified_pitcher: true,
            },
          ],
        },
      });
      return;
    }

    await route.fulfill({
      json: {
        season: 2025,
        series_code: "regular",
        group: "hitters",
        sort_key: "avg",
        qualified_only: true,
        page: 1,
        page_size: 25,
        total_count: 2,
        total_pages: 1,
        snapshot_label: "2025-10-04 regular db snapshot",
        freshness,
        items: [
          {
            rank: 1,
            player_type: "hitter",
            player_id: "lg-홍창기",
            player_name: "홍창기",
            team_code: "LG",
            games: 128,
            plate_appearances: 571,
            innings: null,
            innings_display: null,
            innings_outs: null,
            batting_avg: 0.344,
            hits: 167,
            doubles: 26,
            home_runs: 13,
            stolen_bases: 18,
            ops: 0.923,
            era: null,
            strikeouts: null,
            wins: null,
            whip: null,
            qualified_hitter: true,
            qualified_pitcher: false,
          },
          {
            rank: 2,
            player_type: "hitter",
            player_id: "nc-김주원",
            player_name: "김주원",
            team_code: "NC",
            games: 132,
            plate_appearances: 540,
            innings: null,
            innings_display: null,
            innings_outs: null,
            batting_avg: 0.291,
            hits: 149,
            doubles: 28,
            home_runs: 10,
            stolen_bases: 36,
            ops: 0.812,
            era: null,
            strikeouts: null,
            wins: null,
            whip: null,
            qualified_hitter: true,
            qualified_pitcher: false,
          },
        ],
      },
    });
  });

  await page.route(/http:\/\/127\.0\.0\.1:8000\/api\/players\/ss-%EC%9B%90%ED%83%9C%EC%9D%B8\/season-detail.*/, async (route) => {
    await route.fulfill({
      json: {
        player_key: "ss-원태인",
        player_name: "원태인",
        team_code: "SS",
        group: "pitchers",
        season: 2025,
        series_code: "regular",
        qualified: true,
        totals: {
          games: 29,
          innings_outs: 539,
          innings_display: "179.2",
          hits_allowed: 141,
          walks_allowed: 49,
          strikeouts: 164,
          wins: 14,
          earned_runs: 56,
        },
        metrics: {
          whip: 1.06,
          k_per_9: 8.23,
          bb_per_9: 2.46,
          kbb: 3.35,
        },
        page: 1,
        page_size: 25,
        total_count: 2,
        total_pages: 1,
        freshness,
        seasons: [
          {
            season: 2025,
            team_code: "SS",
            games: 29,
            qualified: true,
            innings_outs: 539,
            innings_display: "179.2",
            wins: 14,
            strikeouts: 164,
            era: 2.81,
            whip: 1.06,
          },
        ],
        logs: [
          {
            game_id: "20251001SSLG0",
            game_date: "2025-10-01",
            series_code: "regular",
            stadium: "잠실",
            result: "W",
            opponent_team_code: "LG",
            innings_outs: 21,
            innings_display: "7.0",
            hits_allowed: 4,
            walks_allowed: 1,
            strikeouts: 8,
            earned_runs: 1,
            decision_code: "승",
          },
        ],
      },
    });
  });

  await page.goto("/seasons/2025/players?series=regular&mode=top5&group=hitters&page=1&pageSize=25");

  await expect(page.getByText("타자 Top 5")).toBeVisible();
  await expect(page.getByRole("button", { name: "선수 기록" })).toBeVisible();
  await expect(page.getByText("도루")).toBeVisible();
  await expect(page.getByText("평균자책점")).toBeVisible();

  await page.getByRole("button", { name: "홈" }).click();
  await expect(page.getByText(/시즌 팀 순위/)).toBeVisible();
  await expect(page.getByRole("button", { name: "LG 트윈스" }).first()).toBeVisible();
  await page.getByRole("button", { name: "LG 트윈스" }).first().click();
  await expect(page.getByText("Teams / Detail")).toBeVisible();
  await expect(page.getByText("OPS+")).toBeVisible();

  await page.getByRole("button", { name: "선수 기록" }).click();
  await page.getByRole("button", { name: "전체 보기" }).click();

  await expect(page.getByText("전체 선수 기록")).toBeVisible();
  await page.getByRole("button", { name: "투수" }).click();
  await expect(page.getByText("179.2")).toBeVisible();
  await expect(page.getByText("원태인")).toBeVisible();
  await page.getByRole("button", { name: "원태인" }).click();
  await expect(page.getByText("Player / Detail")).toBeVisible();
  await expect(page.getByText("7.0")).toBeVisible();

  await page.getByRole("button", { name: "경기 기록" }).click();
  await expect(page.getByText("Games / Browse")).toBeVisible();
  await page.getByRole("button", { name: "3-5" }).click();
  await expect(page.getByText("Games / Detail")).toBeVisible();

  await page.getByRole("button", { name: "홈" }).click();
  await page.selectOption("select", "2026");
  await expect(page.getByText("선택한 시즌 또는 시리즈에는 아직 표시할 데이터가 없습니다.")).toBeVisible();
  await expect(page.getByText("다른 시즌 또는 시리즈를 선택해보세요.")).toBeVisible();
});
