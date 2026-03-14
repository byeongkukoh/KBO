import { expect, test } from "@playwright/test";

const gameResponse = {
  game_id: "20260314WONC0",
  game_date: "2026-03-14",
  status_code: "3",
  stadium: "마산",
  away_team_code: "WO",
  home_team_code: "NC",
  away_score: 6,
  home_score: 8,
  innings: [
    { inning_no: 1, away_runs: 0, home_runs: 2 },
    { inning_no: 2, away_runs: 0, home_runs: 0 },
    { inning_no: 3, away_runs: 0, home_runs: 2 },
    { inning_no: 4, away_runs: 3, home_runs: 0 },
    { inning_no: 5, away_runs: 1, home_runs: 2 },
    { inning_no: 6, away_runs: 0, home_runs: 1 },
    { inning_no: 7, away_runs: 1, home_runs: 0 },
    { inning_no: 8, away_runs: 1, home_runs: 1 },
    { inning_no: 9, away_runs: 0, home_runs: 0 },
  ],
  team_stats: [
    { team_code: "WO", team_name: "키움 히어로즈", runs: 6, hits: 9, errors: 3, walks: 6 },
    { team_code: "NC", team_name: "NC 다이노스", runs: 8, hits: 10, errors: 1, walks: 5 },
  ],
  batting_rows: [
    {
      team_code: "WO",
      player_key: "wo-안치홍",
      player_name: "안치홍",
      at_bats: 4,
      hits: 3,
      doubles: 1,
      triples: 0,
      home_runs: 1,
      walks: 1,
      hit_by_pitch: 0,
      sacrifice_flies: 0,
    },
  ],
  pitching_rows: [
    {
      team_code: "NC",
      player_key: "nc-김녹원",
      player_name: "김녹원",
      innings_outs: 8,
      hits_allowed: 2,
      walks_allowed: 4,
      strikeouts: 2,
    },
  ],
};

const playerResponse = {
  player_key: "wo-안치홍",
  player_name: "안치홍",
  scope: "ingested",
  games_count: 1,
  batting_totals: {
    at_bats: 4,
    hits: 3,
    doubles: 1,
    triples: 0,
    home_runs: 1,
    walks: 1,
    hit_by_pitch: 0,
    sacrifice_flies: 0,
  },
  batting_metrics: {
    singles: 1,
    total_bases: 7,
    avg: 0.75,
    obp: 0.8,
    slg: 1.75,
    ops: 2.55,
  },
  pitching_totals: {
    innings_outs: 0,
    hits_allowed: 0,
    walks_allowed: 0,
    strikeouts: 0,
  },
  pitching_metrics: {
    whip: null,
    k_per_9: null,
    bb_per_9: null,
    kbb: null,
  },
};

test("renders the ingested game verification screen", async ({ page }) => {
  await page.route("http://127.0.0.1:8000/api/games/20260314WONC0", async (route) => {
    await route.fulfill({ json: gameResponse });
  });

  await page.route("http://127.0.0.1:8000/api/players/wo-%EC%95%88%EC%B9%98%ED%99%8D/summary?scope=ingested", async (route) => {
    await route.fulfill({ json: playerResponse });
  });

  await page.goto("/");

  await expect(page.getByTestId("game-id")).toHaveText("20260314WONC0");
  await expect(page.getByTestId("player-wo-안치홍-ops")).toHaveText("2.550");
  await expect(page.getByText("Batting Rows")).toBeVisible();
  await expect(page.getByText("Pitching Rows")).toBeVisible();
});
