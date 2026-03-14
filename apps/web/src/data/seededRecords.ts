import type { LeaderboardCategory } from "../types/records";

export const leaderboardCategories: LeaderboardCategory[] = [
  { key: "avg", label: "타율", playerType: "hitter", statKey: "battingAvg", descending: true, precision: 3 },
  { key: "hits", label: "안타", playerType: "hitter", statKey: "hits", descending: true },
  { key: "doubles", label: "2루타", playerType: "hitter", statKey: "doubles", descending: true },
  { key: "homeRuns", label: "홈런", playerType: "hitter", statKey: "homeRuns", descending: true },
  { key: "stolenBases", label: "도루", playerType: "hitter", statKey: "stolenBases", descending: true },
  { key: "era", label: "평균자책점", playerType: "pitcher", statKey: "era", descending: false, precision: 2 },
  { key: "strikeouts", label: "탈삼진", playerType: "pitcher", statKey: "strikeouts", descending: true },
  { key: "wins", label: "다승", playerType: "pitcher", statKey: "wins", descending: true },
  { key: "whip", label: "WHIP", playerType: "pitcher", statKey: "whip", descending: false, precision: 2 },
];
