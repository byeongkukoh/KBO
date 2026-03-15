import { useEffect, useMemo, useState } from "react";

import { getSeasonPlayerRecords } from "../../../lib/api";
import { getLeaderboardCategories, sortPlayers } from "../../../lib/records";
import type { FullViewMode, PlayerGroup, PlayerRecordsPage, SeasonSnapshot, SeriesCode } from "../../../types/records";
import { LeaderboardCard } from "../components/LeaderboardCard";
import { PlayerComparisonPanel } from "../components/PlayerComparisonPanel";
import { PlayerRecordsTable } from "../components/PlayerRecordsTable";
import { SeasonSelect } from "../components/SeasonSelect";
import { SeriesSelect } from "../components/SeriesSelect";

type PlayersViewProps = {
  season: number;
  seasons: number[];
  seriesCode: SeriesCode;
  onSeasonChange: (season: number) => void;
  onSeriesChange: (series: SeriesCode) => void;
  snapshot: SeasonSnapshot | null;
  emptyMessage?: string | null;
  mode: FullViewMode;
  onModeChange: (mode: FullViewMode) => void;
  qualifiedHittersOnly: boolean;
  onQualifiedHittersOnlyChange: (next: boolean) => void;
  qualifiedPitchersOnly: boolean;
  onQualifiedPitchersOnlyChange: (next: boolean) => void;
  playerGroup: PlayerGroup;
  onPlayerGroupChange: (group: PlayerGroup) => void;
  page: number;
  pageSize: number;
  onPageChange: (page: number) => void;
  onPageSizeChange: (pageSize: number) => void;
  selectedCategoryKey: string;
  onSelectedCategoryKeyChange: (key: string) => void;
  onSelectPlayer: (playerId: string, group: PlayerGroup) => void;
};

export function PlayersView({
  season,
  seasons,
  seriesCode,
  onSeasonChange,
  onSeriesChange,
  snapshot,
  emptyMessage,
  mode,
  onModeChange,
  qualifiedHittersOnly,
  onQualifiedHittersOnlyChange,
  qualifiedPitchersOnly,
  onQualifiedPitchersOnlyChange,
  playerGroup,
  onPlayerGroupChange,
  page,
  pageSize,
  onPageChange,
  onPageSizeChange,
  selectedCategoryKey,
  onSelectedCategoryKeyChange,
  onSelectPlayer,
}: PlayersViewProps) {
  const hitterCategories = getLeaderboardCategories("hitters");
  const pitcherCategories = getLeaderboardCategories("pitchers");
  const fullCategories = getLeaderboardCategories(playerGroup);
  const [recordsPage, setRecordsPage] = useState<PlayerRecordsPage | null>(null);
  const [recordsError, setRecordsError] = useState<string | null>(null);
  const [recordsLoading, setRecordsLoading] = useState(false);
  const selectedCategory = fullCategories.find((category) => category.key === selectedCategoryKey) ?? fullCategories[0];
  const qualifiedOnly = playerGroup === "hitters" ? qualifiedHittersOnly : qualifiedPitchersOnly;

  useEffect(() => {
    if (!fullCategories.some((category) => category.key === selectedCategoryKey)) {
      onSelectedCategoryKeyChange(fullCategories[0].key);
    }
  }, [fullCategories, onSelectedCategoryKeyChange, selectedCategoryKey]);

  useEffect(() => {
    if (mode !== "full") {
      return;
    }
    let active = true;
    async function loadPage(nextPage: number) {
      setRecordsLoading(true);
      setRecordsError(null);
      try {
        const nextRecordsPage = await getSeasonPlayerRecords({
          season,
          seriesCode,
          group: playerGroup,
          sortKey: selectedCategory.key,
          qualifiedOnly,
          page: nextPage,
          pageSize,
        });
        if (!active) {
          return;
        }
        setRecordsPage(nextRecordsPage);
      } catch (caughtError) {
        if (!active) {
          return;
        }
        setRecordsPage(null);
        setRecordsError(caughtError instanceof Error ? caughtError.message : "선수 기록을 불러오지 못했습니다.");
      } finally {
        if (active) {
          setRecordsLoading(false);
        }
      }
    }
    void loadPage(page);
    return () => {
      active = false;
    };
  }, [mode, page, pageSize, playerGroup, qualifiedOnly, season, selectedCategory.key, seriesCode]);

  const topHitters = useMemo(
    () =>
      hitterCategories.map((category) => ({
        category,
        rows: sortPlayers(
          (snapshot?.players ?? []).filter((player) => player.battingAvg !== undefined).filter((player) => (qualifiedHittersOnly ? player.qualifiedHitter : true)),
          category,
        ).slice(0, 5),
      })),
    [hitterCategories, qualifiedHittersOnly, snapshot?.players],
  );
  const topPitchers = useMemo(
    () =>
      pitcherCategories.map((category) => ({
        category,
        rows: sortPlayers(
          (snapshot?.players ?? []).filter((player) => player.era !== undefined).filter((player) => (qualifiedPitchersOnly ? player.qualifiedPitcher : true)),
          category,
        ).slice(0, 5),
      })),
    [pitcherCategories, qualifiedPitchersOnly, snapshot?.players],
  );

  async function handlePageChange(nextPage: number) {
    onPageChange(nextPage);
  }

  return (
    <section className="space-y-8">
      <div className="rounded-[32px] border border-white/10 bg-[radial-gradient(circle_at_top_right,rgba(251,191,36,0.16),transparent_26%),linear-gradient(180deg,rgba(15,23,42,0.96),rgba(2,6,23,0.94))] p-6 shadow-[0_30px_90px_rgba(120,53,15,0.3)] lg:p-8">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <span className="inline-flex rounded-full border border-amber-300/20 bg-amber-300/10 px-3 py-1 text-xs uppercase tracking-[0.28em] text-amber-100/80">Players / Leaderboards</span>
            <h2 className="mt-4 text-3xl font-semibold tracking-tight text-white sm:text-4xl">{season} 시즌 선수 기록</h2>
            <p className="mt-3 max-w-3xl text-sm leading-7 text-slate-300">실제 적재된 시즌 snapshot과 paginated records API를 기준으로 Top 5와 전체 기록표를 탐색합니다.</p>
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <SeasonSelect seasons={seasons} value={season} onChange={onSeasonChange} />
            <SeriesSelect value={seriesCode} onChange={onSeriesChange} />
            <button type="button" className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-white transition hover:border-white/20 hover:bg-white/8" onClick={() => onModeChange(mode === "top5" ? "full" : "top5")}>
              {mode === "top5" ? "전체 보기" : "Top 5 보기"}
            </button>
            <div className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-slate-300">{recordsPage?.snapshotLabel ?? snapshot?.snapshotLabel ?? "데이터 없음"}</div>
          </div>
        </div>
      </div>

      {emptyMessage ? (
        <div className="rounded-[24px] border border-dashed border-white/15 bg-slate-950/35 px-6 py-8 text-sm text-slate-300">
          {emptyMessage}
        </div>
      ) : mode === "top5" ? (
        <div className="space-y-8">
          <section>
            <div className="mb-4 flex items-center justify-between gap-4">
              <h3 className="text-2xl font-semibold text-white">타자 Top 5</h3>
              <button type="button" className={`rounded-full border px-4 py-2 text-sm transition ${qualifiedHittersOnly ? "border-cyan-300/30 bg-cyan-300/12 text-white" : "border-white/10 bg-white/5 text-slate-300"}`} onClick={() => onQualifiedHittersOnlyChange(!qualifiedHittersOnly)}>
                {qualifiedHittersOnly ? "정규타석만 보기" : "전체 타자 보기"}
              </button>
            </div>
            <div className="grid gap-4 xl:grid-cols-2">
              {topHitters.map(({ category, rows }) => (
                <LeaderboardCard key={category.key} category={category} rows={rows} onSelectPlayer={onSelectPlayer} />
              ))}
            </div>
          </section>
          <section>
            <div className="mb-4 flex items-center justify-between gap-4">
              <h3 className="text-2xl font-semibold text-white">투수 Top 5</h3>
              <button type="button" className={`rounded-full border px-4 py-2 text-sm transition ${qualifiedPitchersOnly ? "border-amber-300/30 bg-amber-300/12 text-white" : "border-white/10 bg-white/5 text-slate-300"}`} onClick={() => onQualifiedPitchersOnlyChange(!qualifiedPitchersOnly)}>
                {qualifiedPitchersOnly ? "정규이닝만 보기" : "전체 투수 보기"}
              </button>
            </div>
            <div className="grid gap-4 xl:grid-cols-2">
              {topPitchers.map(({ category, rows }) => (
                <LeaderboardCard key={category.key} category={category} rows={rows} onSelectPlayer={onSelectPlayer} />
              ))}
            </div>
          </section>
        </div>
      ) : (
        <section className="space-y-4">
          <PlayerComparisonPanel season={season} seriesCode={seriesCode} group={playerGroup} candidates={snapshot?.players.filter((player) => (playerGroup === "hitters" ? player.battingAvg !== undefined : player.era !== undefined)) ?? []} />
          <div className="flex flex-col gap-4 rounded-[28px] border border-white/10 bg-slate-950/60 px-5 py-5 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <h3 className="text-xl font-semibold text-white">전체 선수 기록</h3>
              <p className="mt-1 text-sm text-slate-400">타자/투수 버튼과 정렬 기준을 바꿔 실제 페이지네이션 API 결과를 탐색합니다.</p>
            </div>
            <div className="flex flex-wrap gap-2">
              <button type="button" className={`rounded-full border px-3 py-2 text-sm transition ${playerGroup === "hitters" ? "border-cyan-300/35 bg-cyan-300/12 text-white" : "border-white/10 bg-white/5 text-slate-300"}`} onClick={() => onPlayerGroupChange("hitters")}>타자</button>
              <button type="button" className={`rounded-full border px-3 py-2 text-sm transition ${playerGroup === "pitchers" ? "border-amber-300/35 bg-amber-300/12 text-white" : "border-white/10 bg-white/5 text-slate-300"}`} onClick={() => onPlayerGroupChange("pitchers")}>투수</button>
              {fullCategories.map((category) => (
                <button key={category.key} type="button" className={`rounded-full border px-3 py-2 text-sm transition ${selectedCategory.key === category.key ? "border-white/20 bg-white/10 text-white" : "border-white/10 bg-white/5 text-slate-300"}`} onClick={() => onSelectedCategoryKeyChange(category.key)}>
                  {category.label}
                </button>
              ))}
              <button type="button" className={`rounded-full border px-3 py-2 text-sm transition ${playerGroup === "hitters" ? (qualifiedHittersOnly ? "border-cyan-300/35 bg-cyan-300/12 text-white" : "border-white/10 bg-white/5 text-slate-300") : qualifiedPitchersOnly ? "border-amber-300/35 bg-amber-300/12 text-white" : "border-white/10 bg-white/5 text-slate-300"}`} onClick={() => (playerGroup === "hitters" ? onQualifiedHittersOnlyChange(!qualifiedHittersOnly) : onQualifiedPitchersOnlyChange(!qualifiedPitchersOnly))}>
                {playerGroup === "hitters" ? (qualifiedHittersOnly ? "정규타석만" : "전체 타자") : qualifiedPitchersOnly ? "정규이닝만" : "전체 투수"}
              </button>
            </div>
          </div>

          {recordsLoading ? <div className="rounded-[28px] border border-white/10 bg-white/4 px-6 py-10 text-slate-300">전체 기록을 불러오는 중입니다...</div> : null}
          {!recordsLoading && recordsError ? <div className="rounded-[28px] border border-rose-300/20 bg-rose-300/10 px-6 py-10 text-rose-100">{recordsError}</div> : null}
          {!recordsLoading && !recordsError && recordsPage ? (
            <PlayerRecordsTable
              group={playerGroup}
              rows={recordsPage.items}
              page={recordsPage.page}
              pageSize={recordsPage.pageSize}
              totalCount={recordsPage.totalCount}
              totalPages={recordsPage.totalPages}
              onPageChange={handlePageChange}
              onPageSizeChange={onPageSizeChange}
              onSelectPlayer={onSelectPlayer}
            />
          ) : null}
        </section>
      )}
    </section>
  );
}
