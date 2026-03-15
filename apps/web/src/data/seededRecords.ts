import type { LeaderboardCategory } from "../types/records";

export const leaderboardCategories: LeaderboardCategory[] = [
  { key: "avg", label: "타율", playerType: "hitter", statKey: "battingAvg", descending: true, precision: 3 },
  { key: "hits", label: "안타", playerType: "hitter", statKey: "hits", descending: true },
  { key: "doubles", label: "2루타", playerType: "hitter", statKey: "doubles", descending: true },
  { key: "homeRuns", label: "홈런", playerType: "hitter", statKey: "homeRuns", descending: true },
  { key: "stolenBases", label: "도루", playerType: "hitter", statKey: "stolenBases", descending: true },
  { key: "iso", label: "ISO", playerType: "hitter", statKey: "iso", descending: true, precision: 3 },
  { key: "babip", label: "BABIP", playerType: "hitter", statKey: "babip", descending: true, precision: 3 },
  { key: "bbRate", label: "BB%", playerType: "hitter", statKey: "bbRate", descending: true, precision: 3 },
  { key: "kRate", label: "K%", playerType: "hitter", statKey: "kRate", descending: false, precision: 3 },
  { key: "era", label: "평균자책점", playerType: "pitcher", statKey: "era", descending: false, precision: 2 },
  { key: "strikeouts", label: "탈삼진", playerType: "pitcher", statKey: "strikeouts", descending: true },
  { key: "wins", label: "다승", playerType: "pitcher", statKey: "wins", descending: true },
  { key: "whip", label: "WHIP", playerType: "pitcher", statKey: "whip", descending: false, precision: 2 },
  { key: "kPer9", label: "K/9", playerType: "pitcher", statKey: "kPer9", descending: true, precision: 2 },
  { key: "bbPer9", label: "BB/9", playerType: "pitcher", statKey: "bbPer9", descending: false, precision: 2 },
  { key: "kbb", label: "K/BB", playerType: "pitcher", statKey: "kbb", descending: true, precision: 2 },
];
