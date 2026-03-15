import type { GameDetail, PlayerSummary } from "../types/game";
import type { LeaderboardPlayer, PlayerGroup, PlayerRecordRow, PlayerRecordsPage, SeasonSnapshot, SeriesCode, TeamStanding } from "../types/records";

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000/api").replace(/\/$/, "");

async function requestJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`);

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed with ${response.status}`);
  }

  return (await response.json()) as T;
}

export function getGameDetail(gameId: string): Promise<GameDetail> {
  return requestJson<GameDetail>(`/games/${encodeURIComponent(gameId)}`);
}

export function getPlayerSummary(playerKey: string): Promise<PlayerSummary> {
  return requestJson<PlayerSummary>(`/players/${encodeURIComponent(playerKey)}/summary?scope=ingested`);
}

type ApiSeasonList = {
  seasons: number[];
};

type ApiTeamStanding = {
  rank: number;
  games: number;
  team_code: string;
  team_name: string;
  wins: number;
  losses: number;
  draws: number;
  win_pct: number | null;
  games_back: number;
  runs_scored: number;
  runs_allowed: number;
  run_diff: number;
  hits: number;
  doubles: number;
  batting_avg: number | null;
  obp: number | null;
  slg: number | null;
  ops: number | null;
  home_runs: number;
  stolen_bases: number | null;
  era: number | null;
  whip: number | null;
  last_ten: string;
  streak: string;
};

type ApiLeaderboardPlayer = {
  player_id: string;
  player_name: string;
  team_code: string;
  games: number;
  plate_appearances: number | null;
  innings: number | null;
  batting_avg: number | null;
  hits: number | null;
  doubles: number | null;
  home_runs: number | null;
  stolen_bases: number | null;
  ops: number | null;
  era: number | null;
  strikeouts: number | null;
  wins: number | null;
  whip: number | null;
  qualified_hitter: boolean;
  qualified_pitcher: boolean;
};

type ApiSeasonSnapshot = {
  season: number;
  snapshot_label: string;
  standings: ApiTeamStanding[];
  players: ApiLeaderboardPlayer[];
};

type ApiPlayerRecordRow = {
  rank: number;
  player_type: string;
  player_id: string;
  player_name: string;
  team_code: string;
  games: number;
  plate_appearances: number | null;
  innings: number | null;
  innings_display: string | null;
  innings_outs: number | null;
  batting_avg: number | null;
  hits: number | null;
  doubles: number | null;
  home_runs: number | null;
  stolen_bases: number | null;
  ops: number | null;
  era: number | null;
  strikeouts: number | null;
  wins: number | null;
  whip: number | null;
  qualified_hitter: boolean;
  qualified_pitcher: boolean;
};

type ApiPlayerRecordsPage = {
  season: number;
  series_code: string | null;
  group: string;
  sort_key: string;
  qualified_only: boolean;
  page: number;
  page_size: number;
  total_count: number;
  total_pages: number;
  snapshot_label: string;
  items: ApiPlayerRecordRow[];
};

function adaptTeamStanding(team: ApiTeamStanding): TeamStanding {
  return {
    rank: team.rank,
    games: team.games,
    teamCode: team.team_code,
    teamName: team.team_name,
    wins: team.wins,
    losses: team.losses,
    draws: team.draws,
    winPct: team.win_pct ?? 0,
    gamesBack: team.games_back,
    runsScored: team.runs_scored,
    runsAllowed: team.runs_allowed,
    runDiff: team.run_diff,
    hits: team.hits,
    doubles: team.doubles,
    battingAvg: team.batting_avg ?? 0,
    obp: team.obp ?? 0,
    slg: team.slg ?? 0,
    ops: team.ops ?? 0,
    homeRuns: team.home_runs,
    stolenBases: team.stolen_bases ?? 0,
    era: team.era ?? 0,
    whip: team.whip ?? 0,
    lastTen: team.last_ten,
    streak: team.streak,
  };
}

function adaptLeaderboardPlayer(player: ApiLeaderboardPlayer): LeaderboardPlayer {
  return {
    playerId: player.player_id,
    playerName: player.player_name,
    teamCode: player.team_code,
    games: player.games,
    plateAppearances: player.plate_appearances ?? undefined,
    innings: player.innings ?? undefined,
    battingAvg: player.batting_avg ?? undefined,
    hits: player.hits ?? undefined,
    doubles: player.doubles ?? undefined,
    homeRuns: player.home_runs ?? undefined,
    stolenBases: player.stolen_bases ?? undefined,
    ops: player.ops ?? undefined,
    era: player.era ?? undefined,
    strikeouts: player.strikeouts ?? undefined,
    wins: player.wins ?? undefined,
    whip: player.whip ?? undefined,
    qualifiedHitter: player.qualified_hitter,
    qualifiedPitcher: player.qualified_pitcher,
  };
}

function adaptPlayerRecordRow(player: ApiPlayerRecordRow): PlayerRecordRow {
  return {
    rank: player.rank,
    playerType: player.player_type === "pitcher" ? "pitcher" : "hitter",
    playerId: player.player_id,
    playerName: player.player_name,
    teamCode: player.team_code,
    games: player.games,
    plateAppearances: player.plate_appearances ?? undefined,
    innings: player.innings ?? undefined,
    inningsDisplay: player.innings_display ?? undefined,
    inningsOuts: player.innings_outs ?? undefined,
    battingAvg: player.batting_avg ?? undefined,
    hits: player.hits ?? undefined,
    doubles: player.doubles ?? undefined,
    homeRuns: player.home_runs ?? undefined,
    stolenBases: player.stolen_bases ?? undefined,
    ops: player.ops ?? undefined,
    era: player.era ?? undefined,
    strikeouts: player.strikeouts ?? undefined,
    wins: player.wins ?? undefined,
    whip: player.whip ?? undefined,
    qualifiedHitter: player.qualified_hitter,
    qualifiedPitcher: player.qualified_pitcher,
  };
}

export async function getSeasons(): Promise<number[]> {
  const response = await requestJson<ApiSeasonList>("/seasons");
  return response.seasons;
}

export async function getSeasonSnapshot(season: number, seriesCode: SeriesCode): Promise<SeasonSnapshot> {
  const response = await requestJson<ApiSeasonSnapshot>(`/seasons/${season}/snapshot?series_code=${encodeURIComponent(seriesCode)}`);
  return {
    season: response.season,
    snapshotLabel: response.snapshot_label,
    standings: response.standings.map(adaptTeamStanding),
    players: response.players.map(adaptLeaderboardPlayer),
  };
}

export async function getSeasonPlayerRecords(options: {
  season: number;
  seriesCode: SeriesCode;
  group: PlayerGroup;
  sortKey: string;
  qualifiedOnly: boolean;
  page: number;
  pageSize: number;
}): Promise<PlayerRecordsPage> {
  const params = new URLSearchParams({
    group: options.group,
    sort_key: options.sortKey,
    qualified_only: String(options.qualifiedOnly),
    page: String(options.page),
    page_size: String(options.pageSize),
    series_code: options.seriesCode,
  });
  const response = await requestJson<ApiPlayerRecordsPage>(`/seasons/${options.season}/player-records?${params.toString()}`);
  return {
    season: response.season,
    seriesCode: response.series_code === null ? undefined : (response.series_code as SeriesCode),
    group: response.group as PlayerGroup,
    sortKey: response.sort_key,
    qualifiedOnly: response.qualified_only,
    page: response.page,
    pageSize: response.page_size,
    totalCount: response.total_count,
    totalPages: response.total_pages,
    snapshotLabel: response.snapshot_label,
    items: response.items.map(adaptPlayerRecordRow),
  };
}
