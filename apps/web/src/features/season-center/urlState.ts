import type { AppView, FullViewMode, PlayerGroup, SeriesCode } from "../../types/records";

export type SeasonCenterUrlState = {
  view: AppView;
  season?: number;
  seriesCode: SeriesCode;
  mode: FullViewMode;
  group: PlayerGroup;
  sortKey?: string;
  qualifiedHittersOnly: boolean;
  qualifiedPitchersOnly: boolean;
  page: number;
  pageSize: number;
  playerKey?: string;
};

const defaultState: SeasonCenterUrlState = {
  view: "home",
  seriesCode: "regular",
  mode: "top5",
  group: "hitters",
  qualifiedHittersOnly: true,
  qualifiedPitchersOnly: true,
  page: 1,
  pageSize: 25,
};

export function readUrlState(): SeasonCenterUrlState {
  const params = new URLSearchParams(window.location.search);
  const view = params.get("view");
  const series = params.get("series");
  const mode = params.get("mode");
  const group = params.get("group");
  const season = params.get("season");
  const page = params.get("page");
  const pageSize = params.get("pageSize");

  return {
    view: view === "players" || view === "player" ? view : "home",
    season: season ? Number(season) : undefined,
    seriesCode: series === "preseason" || series === "postseason" ? series : "regular",
    mode: mode === "full" ? "full" : "top5",
    group: group === "pitchers" ? "pitchers" : "hitters",
    sortKey: params.get("sort") ?? undefined,
    qualifiedHittersOnly: params.get("qh") !== "0",
    qualifiedPitchersOnly: params.get("qp") !== "0",
    page: page ? Math.max(Number(page), 1) : 1,
    pageSize: pageSize ? Math.max(Number(pageSize), 1) : 25,
    playerKey: params.get("player") ?? undefined,
  };
}

export function writeUrlState(next: Partial<SeasonCenterUrlState>) {
  const current = { ...defaultState, ...readUrlState(), ...next };
  const params = new URLSearchParams();
  params.set("view", current.view);
  params.set("series", current.seriesCode);
  params.set("mode", current.mode);
  params.set("group", current.group);
  params.set("qh", current.qualifiedHittersOnly ? "1" : "0");
  params.set("qp", current.qualifiedPitchersOnly ? "1" : "0");
  params.set("page", String(current.page));
  params.set("pageSize", String(current.pageSize));
  if (current.season !== undefined) {
    params.set("season", String(current.season));
  }
  if (current.sortKey) {
    params.set("sort", current.sortKey);
  }
  if (current.playerKey) {
    params.set("player", current.playerKey);
  }
  window.history.replaceState({}, "", `${window.location.pathname}?${params.toString()}`);
}
