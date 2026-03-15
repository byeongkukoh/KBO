import { useEffect, useState } from "react";

import { getSeasonSnapshot as fetchSeasonSnapshot, getSeasons } from "../../lib/api";
import type { AppView, SeasonSnapshot, SeriesCode } from "../../types/records";
import { Sidebar } from "./components/Sidebar";
import { HomeView } from "./views/HomeView";
import { PlayersView } from "./views/PlayersView";

const currentYear = new Date().getFullYear();

function selectDefaultSeason(seasons: number[]): number | null {
  if (seasons.length === 0) {
    return null;
  }
  if (seasons.includes(currentYear)) {
    return currentYear;
  }
  return seasons[0];
}

export function SeasonCenterPage() {
  const [view, setView] = useState<AppView>("home");
  const [season, setSeason] = useState<number | null>(null);
  const [seriesCode, setSeriesCode] = useState<SeriesCode>("regular");
  const [seasons, setSeasons] = useState<number[]>([]);
  const [snapshot, setSnapshot] = useState<SeasonSnapshot | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    async function loadSeasons() {
      setIsLoading(true);
      setError(null);
      try {
        const nextSeasons = await getSeasons();
        if (!active) {
          return;
        }
        setSeasons(nextSeasons);
        setSeason((current) => current ?? selectDefaultSeason(nextSeasons));
      } catch (caughtError) {
        if (!active) {
          return;
        }
        const message = caughtError instanceof Error ? caughtError.message : "시즌 목록을 불러오지 못했습니다.";
        setError(message);
        setIsLoading(false);
      }
    }

    void loadSeasons();
    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    if (season === null) {
      return;
    }
    const selectedSeason = season;
    let active = true;
    async function loadSnapshot() {
      setIsLoading(true);
      setError(null);
      try {
        const nextSnapshot = await fetchSeasonSnapshot(selectedSeason, seriesCode);
        if (!active) {
          return;
        }
        setSnapshot(nextSnapshot);
      } catch (caughtError) {
        if (!active) {
          return;
        }
        const message = caughtError instanceof Error ? caughtError.message : "시즌 snapshot을 불러오지 못했습니다.";
        setSnapshot(null);
        setError(message);
      } finally {
        if (active) {
          setIsLoading(false);
        }
      }
    }

    void loadSnapshot();
    return () => {
      active = false;
    };
  }, [season, seriesCode]);

  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top_left,rgba(56,189,248,0.12),transparent_22%),radial-gradient(circle_at_bottom_right,rgba(251,191,36,0.12),transparent_20%),linear-gradient(180deg,#020617_0%,#0f172a_46%,#020617_100%)] text-slate-50">
      <section className="mx-auto flex max-w-[1500px] flex-col gap-6 px-4 py-5 sm:px-6 lg:flex-row lg:px-8 lg:py-8">
        <Sidebar view={view} onChange={setView} seriesCode={seriesCode} />
        <div className="min-w-0 flex-1">
          <div className="mb-6 rounded-[28px] border border-white/8 bg-white/[0.03] px-5 py-4 text-sm leading-6 text-slate-300 shadow-[0_20px_80px_rgba(2,6,23,0.28)]">
            <span className="font-semibold text-white">DB snapshot</span> 기준 데이터입니다. 현재는 PostgreSQL에 적재된 실제 2025 시즌 실데이터를 기준으로 시리즈별 집계를 보여줍니다.
          </div>

          {isLoading ? <div className="rounded-[28px] border border-white/10 bg-white/4 px-6 py-10 text-slate-300">시즌 데이터를 불러오는 중입니다...</div> : null}
          {!isLoading && error ? <div className="rounded-[28px] border border-rose-300/20 bg-rose-300/10 px-6 py-10 text-rose-100">{error}</div> : null}
          {!isLoading && !error && snapshot && season !== null
            ? view === "home"
              ? <HomeView season={season} seasons={seasons} seriesCode={seriesCode} onSeasonChange={setSeason} onSeriesChange={setSeriesCode} snapshot={snapshot} />
              : <PlayersView season={season} seasons={seasons} seriesCode={seriesCode} onSeasonChange={setSeason} onSeriesChange={setSeriesCode} snapshot={snapshot} />
            : null}
        </div>
      </section>
    </main>
  );
}
