export type InningScore = {
  inning_no: number;
  away_runs: number;
  home_runs: number;
};

export type TeamStat = {
  team_code: string;
  team_name: string;
  runs: number;
  hits: number;
  errors: number;
  walks: number;
};

export type BattingRow = {
  team_code: string;
  player_key: string;
  player_name: string;
  at_bats: number;
  hits: number;
  doubles: number;
  triples: number;
  home_runs: number;
  walks: number;
  hit_by_pitch: number;
  sacrifice_flies: number;
};

export type PitchingRow = {
  team_code: string;
  player_key: string;
  player_name: string;
  innings_outs: number;
  hits_allowed: number;
  walks_allowed: number;
  strikeouts: number;
};

export type GameDetail = {
  game_id: string;
  game_date: string;
  status_code: string;
  stadium: string;
  away_team_code: string;
  home_team_code: string;
  away_score: number;
  home_score: number;
  innings: InningScore[];
  team_stats: TeamStat[];
  batting_rows: BattingRow[];
  pitching_rows: PitchingRow[];
};

export type BattingTotals = {
  at_bats: number;
  hits: number;
  doubles: number;
  triples: number;
  home_runs: number;
  walks: number;
  hit_by_pitch: number;
  sacrifice_flies: number;
};

export type PitchingTotals = {
  innings_outs: number;
  hits_allowed: number;
  walks_allowed: number;
  strikeouts: number;
};

export type PlayerSummary = {
  player_key: string;
  player_name: string;
  scope: string;
  games_count: number;
  batting_totals: BattingTotals;
  batting_metrics: Record<string, number | null>;
  pitching_totals: PitchingTotals;
  pitching_metrics: Record<string, number | null>;
};
