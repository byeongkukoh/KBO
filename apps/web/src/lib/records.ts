import { leaderboardCategories, seededSeasons } from "../data/seededRecords";
import type { LeaderboardCategory, LeaderboardPlayer, SeasonSnapshot, TeamStanding } from "../types/records";

export type TeamSortKey = "winPct" | "hits" | "doubles" | "battingAvg" | "ops" | "era";
export type PlayerGroup = "hitters" | "pitchers";
export type FullViewMode = "top5" | "full";

export function getAvailableSeasons(): number[] {
  return seededSeasons.map((season) => season.season).sort((a, b) => b - a);
}

export function getDefaultSeason(currentYear: number): number {
  const seasons = getAvailableSeasons();
  if (seasons.includes(currentYear)) {
    return currentYear;
  }
  return seasons[0];
}

export function getSeasonSnapshot(season: number): SeasonSnapshot {
  return seededSeasons.find((item) => item.season === season) ?? seededSeasons[0];
}

export function sortStandings(rows: TeamStanding[], sortKey: TeamSortKey): TeamStanding[] {
  const sorted = [...rows].sort((left, right) => {
    if (sortKey === "era") {
      return left.era - right.era || right.winPct - left.winPct;
    }

    return right[sortKey] - left[sortKey] || right.winPct - left.winPct;
  });

  return sorted;
}

export function getLeaderboardCategories(group: PlayerGroup): LeaderboardCategory[] {
  return leaderboardCategories.filter((category) => category.playerType === (group === "hitters" ? "hitter" : "pitcher"));
}

export function filterPlayers(players: LeaderboardPlayer[], group: PlayerGroup, qualifiedOnly: boolean): LeaderboardPlayer[] {
  return players.filter((player) => {
    if (group === "hitters") {
      if (player.battingAvg === undefined) {
        return false;
      }
      return qualifiedOnly ? player.qualifiedHitter : true;
    }

    if (player.era === undefined) {
      return false;
    }

    return qualifiedOnly ? player.qualifiedPitcher : true;
  });
}

export function sortPlayers(players: LeaderboardPlayer[], category: LeaderboardCategory): LeaderboardPlayer[] {
  return [...players].sort((left, right) => {
    const leftValue = Number(left[category.statKey] ?? 0);
    const rightValue = Number(right[category.statKey] ?? 0);
    if (category.descending) {
      return rightValue - leftValue || left.games - right.games;
    }
    return leftValue - rightValue || right.games - left.games;
  });
}

export function formatStat(value: number | undefined, precision = 0): string {
  if (value === undefined) {
    return "-";
  }

  if (precision === 0) {
    return `${value}`;
  }

  return value.toFixed(precision);
}
