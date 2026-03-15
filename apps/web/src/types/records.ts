export type AppView = "home" | "players" | "player" | "team" | "games" | "game";

export type TeamStanding = {
  teamCode: string;
  teamName: string;
  rank: number;
  games: number;
  wins: number;
  losses: number;
  draws: number;
  winPct: number;
  gamesBack: number;
  runsScored: number;
  runsAllowed: number;
  runDiff: number;
  hits: number;
  doubles: number;
  battingAvg: number;
  obp: number;
  slg: number;
  ops: number;
  homeRuns: number;
  stolenBases: number;
  era: number;
  whip: number;
  lastTen: string;
  streak: string;
};

export type LeaderboardPlayer = {
  playerId: string;
  playerName: string;
  teamCode: string;
  games: number;
  plateAppearances?: number;
  innings?: number;
  battingAvg?: number;
  hits?: number;
  doubles?: number;
  homeRuns?: number;
  stolenBases?: number;
  ops?: number;
  iso?: number;
  babip?: number;
  bbRate?: number;
  kRate?: number;
  era?: number;
  strikeouts?: number;
  wins?: number;
  whip?: number;
  kPer9?: number;
  bbPer9?: number;
  kbb?: number;
  qualifiedHitter: boolean;
  qualifiedPitcher: boolean;
};

export type PlayerRecordRow = {
  rank: number;
  playerType: "hitter" | "pitcher";
  playerId: string;
  playerName: string;
  teamCode: string;
  games: number;
  plateAppearances?: number;
  innings?: number;
  inningsDisplay?: string;
  inningsOuts?: number;
  battingAvg?: number;
  hits?: number;
  doubles?: number;
  homeRuns?: number;
  stolenBases?: number;
  ops?: number;
  iso?: number;
  babip?: number;
  bbRate?: number;
  kRate?: number;
  era?: number;
  strikeouts?: number;
  wins?: number;
  whip?: number;
  kPer9?: number;
  bbPer9?: number;
  kbb?: number;
  qualifiedHitter: boolean;
  qualifiedPitcher: boolean;
};

export type LeaderboardCategory = {
  key: string;
  label: string;
  playerType: "hitter" | "pitcher";
  statKey: keyof LeaderboardPlayer;
  descending: boolean;
  precision?: number;
};

export type SeasonSnapshot = {
  season: number;
  snapshotLabel: string;
  standings: TeamStanding[];
  players: LeaderboardPlayer[];
};

export type SeriesCode = "preseason" | "regular" | "postseason";

export type PlayerGroup = "hitters" | "pitchers";
export type FullViewMode = "top5" | "full";

export type PlayerRecordsPage = {
  season: number;
  seriesCode?: SeriesCode;
  group: PlayerGroup;
  sortKey: string;
  qualifiedOnly: boolean;
  page: number;
  pageSize: number;
  totalCount: number;
  totalPages: number;
  snapshotLabel: string;
  items: PlayerRecordRow[];
};

export type PlayerDetailLog = {
  gameId: string;
  gameDate: string;
  seriesCode: string;
  stadium: string;
  result: string;
  opponentTeamCode: string;
  positionCode?: string;
  plateAppearances?: number;
  atBats?: number;
  hits?: number;
  doubles?: number;
  triples?: number;
  homeRuns?: number;
  stolenBases?: number;
  walks?: number;
  runsBattedIn?: number;
  strikeouts?: number;
  inningsOuts?: number;
  inningsDisplay?: string;
  hitsAllowed?: number;
  walksAllowed?: number;
  earnedRuns?: number;
  decisionCode?: string;
};

export type PlayerDetail = {
  playerKey: string;
  playerName: string;
  teamCode: string;
  group: PlayerGroup;
  season: number;
  seriesCode?: SeriesCode;
  qualified: boolean;
  totals: Record<string, number | string>;
  metrics: Record<string, number | null>;
  page: number;
  pageSize: number;
  totalCount: number;
  totalPages: number;
  seasons: Array<Record<string, string | number | boolean | null>>;
  logs: PlayerDetailLog[];
};

export type TeamSeasonDetail = {
  season: number;
  seriesCode?: SeriesCode;
  teamCode: string;
  teamName: string;
  wins: number;
  losses: number;
  draws: number;
  winPct?: number;
  runsScored: number;
  runsAllowed: number;
  runDiff: number;
  hits: number;
  doubles: number;
  stolenBases: number;
  battingAvg?: number;
  ops?: number;
  era?: number;
  whip?: number;
  opsPlus?: number;
  eraPlus?: number;
  lastTen: string;
  streak: string;
  recentGames: Array<{
    gameId: string;
    gameDate: string;
    seriesCode: string;
    stadium: string;
    result: string;
    opponentTeamCode: string;
    teamScore: number;
    opponentScore: number;
  }>;
};

export type GameListItem = {
  gameId: string;
  gameDate: string;
  seriesCode: string;
  seriesName: string;
  stadium: string;
  awayTeamCode: string;
  homeTeamCode: string;
  awayScore: number;
  homeScore: number;
  statusCode: string;
};

export type GameListPage = {
  season: number;
  seriesCode?: SeriesCode;
  teamCode?: string;
  gameDate?: string;
  page: number;
  pageSize: number;
  totalCount: number;
  totalPages: number;
  items: GameListItem[];
};
