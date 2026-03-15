export type AppView = "home" | "players";

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
  era?: number;
  strikeouts?: number;
  wins?: number;
  whip?: number;
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
  era?: number;
  strikeouts?: number;
  wins?: number;
  whip?: number;
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
