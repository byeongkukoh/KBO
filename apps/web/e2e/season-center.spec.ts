import { expect, test } from "@playwright/test";

test("renders db-backed standings and player records", async ({ page }) => {
  await page.route("http://127.0.0.1:8000/api/seasons", async (route) => {
    await route.fulfill({ json: { seasons: [2025] } });
  });

  await page.route("http://127.0.0.1:8000/api/seasons/2025/snapshot?series_code=regular", async (route) => {
    await route.fulfill({
      json: {
        season: 2025,
        snapshot_label: "2025-10-04 regular db snapshot",
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

  await page.goto("/");

  await expect(page.getByText(/시즌 팀 순위/)).toBeVisible();
  await expect(page.getByRole("heading", { name: "LG 트윈스" })).toBeVisible();
  await expect(page.getByRole("button", { name: "선수 기록" })).toBeVisible();

  await page.getByRole("button", { name: "선수 기록" }).click();

  await expect(page.getByText("타자 Top 5")).toBeVisible();
  await expect(page.getByText("도루")).toBeVisible();
  await expect(page.getByText("평균자책점")).toBeVisible();

  await page.getByRole("button", { name: "전체 보기" }).click();

  await expect(page.getByText("전체 선수 기록")).toBeVisible();
  await page.getByRole("button", { name: "투수" }).click();
  await expect(page.getByText("원태인")).toBeVisible();
});
