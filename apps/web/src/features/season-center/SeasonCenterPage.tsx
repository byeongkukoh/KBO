import { useEffect, useState } from "react";

import { getGameDetail, getGamesPage, getPlayerSeasonDetail, getSeasonSnapshot as fetchSeasonSnapshot, getSeasons, getTeamSeasonDetail } from "../../lib/api";
import type { FullViewMode, GameListPage, PlayerDetail, PlayerGroup, SeasonSnapshot, SeriesCode, TeamSeasonDetail } from "../../types/records";
import type { AppView } from "../../types/records";
import type { GameDetail } from "../../types/game";
import { Sidebar } from "./components/Sidebar";
import { GamesView } from "./views/GamesView";
import { GameDetailView } from "./views/GameDetailView";
import { HomeView } from "./views/HomeView";
import { PlayerDetailView } from "./views/PlayerDetailView";
import { PlayersView } from "./views/PlayersView";
import { TeamDetailView } from "./views/TeamDetailView";
import { readUrlState, writeUrlState } from "./urlState";

const currentYear = new Date().getFullYear();

function selectDefaultSeason(seasons: number[]): number | null {
  if (seasons.length === 0) return null;
  if (seasons.includes(currentYear)) return currentYear;
  return seasons[0];
}

function buildFreshnessLabel(data: { latestGameDate?: string; lastSuccessfulSyncAt?: string; contextUpdatedAt?: string } | undefined) {
  if (!data) return "동기화 정보 없음";
  const parts = [];
  if (data.latestGameDate) parts.push(`데이터 기준일 ${data.latestGameDate}`);
  if (data.lastSuccessfulSyncAt) parts.push(`마지막 적재 ${data.lastSuccessfulSyncAt}`);
  if (data.contextUpdatedAt) parts.push(`컨텍스트 갱신 ${data.contextUpdatedAt}`);
  return parts.join(" · ") || "동기화 정보 없음";
}

export function SeasonCenterPage() {
  const initialUrlState = readUrlState();
  const [view, setView] = useState<AppView>(initialUrlState.view);
  const [season, setSeason] = useState<number | null>(initialUrlState.season ?? null);
  const [seriesCode, setSeriesCode] = useState<SeriesCode>(initialUrlState.seriesCode);
  const [mode, setMode] = useState<FullViewMode>(initialUrlState.mode);
  const [playerGroup, setPlayerGroup] = useState<PlayerGroup>(initialUrlState.group);
  const [qualifiedHittersOnly, setQualifiedHittersOnly] = useState(initialUrlState.qualifiedHittersOnly);
  const [qualifiedPitchersOnly, setQualifiedPitchersOnly] = useState(initialUrlState.qualifiedPitchersOnly);
  const [page, setPage] = useState(initialUrlState.page);
  const [pageSize, setPageSize] = useState(initialUrlState.pageSize);
  const [selectedCategoryKey, setSelectedCategoryKey] = useState(initialUrlState.sortKey ?? (playerGroup === "pitchers" ? "era" : "avg"));
  const [selectedPlayerKey, setSelectedPlayerKey] = useState<string | undefined>(initialUrlState.playerKey);
  const [selectedTeamCode, setSelectedTeamCode] = useState<string | undefined>(initialUrlState.teamCode);
  const [selectedGameId, setSelectedGameId] = useState<string | undefined>(initialUrlState.gameId);
  const [seasons, setSeasons] = useState<number[]>([]);
  const [snapshot, setSnapshot] = useState<SeasonSnapshot | null>(null);
  const [playerDetail, setPlayerDetail] = useState<PlayerDetail | null>(null);
  const [teamDetail, setTeamDetail] = useState<TeamSeasonDetail | null>(null);
  const [gamesPage, setGamesPage] = useState<GameListPage | null>(null);
  const [gameDetail, setGameDetail] = useState<GameDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const activeFreshness = snapshot?.freshness ?? playerDetail?.freshness ?? teamDetail?.freshness ?? gamesPage?.freshness ?? gameDetail?.freshness;

  useEffect(() => {
    writeUrlState({
      view,
      season: season ?? undefined,
      seriesCode,
      mode,
      group: playerGroup,
      sortKey: selectedCategoryKey,
      qualifiedHittersOnly,
      qualifiedPitchersOnly,
      page,
      pageSize,
      playerKey: selectedPlayerKey,
      teamCode: selectedTeamCode,
      gameId: selectedGameId,
    });
  }, [view, season, seriesCode, mode, playerGroup, selectedCategoryKey, qualifiedHittersOnly, qualifiedPitchersOnly, page, pageSize, selectedPlayerKey, selectedTeamCode, selectedGameId]);

  useEffect(() => {
    let active = true;
    async function loadSeasons() {
      setIsLoading(true);
      setError(null);
      try {
        const nextSeasons = await getSeasons();
        if (!active) return;
        setSeasons(nextSeasons);
        setSeason((current) => current ?? selectDefaultSeason(nextSeasons));
      } catch (caughtError) {
        if (!active) return;
        setError(caughtError instanceof Error ? caughtError.message : "시즌 목록을 불러오지 못했습니다.");
        setIsLoading(false);
      }
    }
    void loadSeasons();
    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    if (season === null || view !== "home") return;
    const selectedSeason = season;
    let active = true;
    async function loadSnapshot() {
      setIsLoading(true);
      setError(null);
      try {
        const nextSnapshot = await fetchSeasonSnapshot(selectedSeason, seriesCode);
        if (!active) return;
        setSnapshot(nextSnapshot);
      } catch (caughtError) {
        if (!active) return;
        setSnapshot(null);
        setError(caughtError instanceof Error ? caughtError.message : "시즌 snapshot을 불러오지 못했습니다.");
      } finally {
        if (active) setIsLoading(false);
      }
    }
    void loadSnapshot();
    return () => {
      active = false;
    };
  }, [season, seriesCode, view]);

  useEffect(() => {
    if (season === null || view !== "players") return;
    const selectedSeason = season;
    let active = true;
    async function loadSnapshot() {
      setIsLoading(true);
      setError(null);
      try {
        const nextSnapshot = await fetchSeasonSnapshot(selectedSeason, seriesCode);
        if (!active) return;
        setSnapshot(nextSnapshot);
      } catch (caughtError) {
        if (!active) return;
        setSnapshot(null);
        setError(caughtError instanceof Error ? caughtError.message : "시즌 snapshot을 불러오지 못했습니다.");
      } finally {
        if (active) setIsLoading(false);
      }
    }
    void loadSnapshot();
    return () => {
      active = false;
    };
  }, [season, seriesCode, view]);

  useEffect(() => {
    if (season === null || view !== "player" || !selectedPlayerKey) return;
    const selectedSeason = season;
    const playerKey = selectedPlayerKey;
    let active = true;
    async function loadPlayerDetail() {
      setIsLoading(true);
      setError(null);
      try {
        const detail = await getPlayerSeasonDetail({ playerKey, season: selectedSeason, seriesCode, group: playerGroup, page, pageSize });
        if (!active) return;
        setPlayerDetail(detail);
      } catch (caughtError) {
        if (!active) return;
        setPlayerDetail(null);
        setError(caughtError instanceof Error ? caughtError.message : "선수 상세를 불러오지 못했습니다.");
      } finally {
        if (active) setIsLoading(false);
      }
    }
    void loadPlayerDetail();
    return () => {
      active = false;
    };
  }, [season, seriesCode, playerGroup, page, pageSize, selectedPlayerKey, view]);

  useEffect(() => {
    if (season === null || view !== "team" || !selectedTeamCode) return;
    const selectedSeason = season;
    const teamCode = selectedTeamCode;
    let active = true;
    async function loadTeam() {
      setIsLoading(true);
      setError(null);
      try {
        const detail = await getTeamSeasonDetail({ teamCode, season: selectedSeason, seriesCode });
        if (!active) return;
        setTeamDetail(detail);
      } catch (caughtError) {
        if (!active) return;
        setTeamDetail(null);
        setError(caughtError instanceof Error ? caughtError.message : "팀 상세를 불러오지 못했습니다.");
      } finally {
        if (active) setIsLoading(false);
      }
    }
    void loadTeam();
    return () => {
      active = false;
    };
  }, [season, seriesCode, selectedTeamCode, view]);

  useEffect(() => {
    if (season === null || view !== "games") return;
    const selectedSeason = season;
    let active = true;
    async function loadGames() {
      setIsLoading(true);
      setError(null);
      try {
        const result = await getGamesPage({ season: selectedSeason, seriesCode, page, pageSize });
        if (!active) return;
        setGamesPage(result);
      } catch (caughtError) {
        if (!active) return;
        setGamesPage(null);
        setError(caughtError instanceof Error ? caughtError.message : "경기 목록을 불러오지 못했습니다.");
      } finally {
        if (active) setIsLoading(false);
      }
    }
    void loadGames();
    return () => {
      active = false;
    };
  }, [season, seriesCode, page, pageSize, view]);

  useEffect(() => {
    if (view !== "game" || !selectedGameId) return;
    const gameId = selectedGameId;
    let active = true;
    async function loadGame() {
      setIsLoading(true);
      setError(null);
      try {
        const result = await getGameDetail(gameId);
        if (!active) return;
        setGameDetail(result);
      } catch (caughtError) {
        if (!active) return;
        setGameDetail(null);
        setError(caughtError instanceof Error ? caughtError.message : "경기 상세를 불러오지 못했습니다.");
      } finally {
        if (active) setIsLoading(false);
      }
    }
    void loadGame();
    return () => {
      active = false;
    };
  }, [selectedGameId, view]);

  function resetPaging() {
    setPage(1);
  }

  function handleSeasonChange(nextSeason: number) { setSeason(nextSeason); resetPaging(); }
  function handleSeriesChange(nextSeries: SeriesCode) { setSeriesCode(nextSeries); resetPaging(); }
  function handleSelectPlayer(playerId: string, group: PlayerGroup) { setSelectedPlayerKey(playerId); setPlayerGroup(group); setView("player"); resetPaging(); }
  function handleSelectTeam(teamCode: string) { setSelectedTeamCode(teamCode); setView("team"); resetPaging(); }
  function handleOpenGame(gameId: string) { setSelectedGameId(gameId); setView("game"); }

  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top_left,rgba(56,189,248,0.12),transparent_22%),radial-gradient(circle_at_bottom_right,rgba(251,191,36,0.12),transparent_20%),linear-gradient(180deg,#020617_0%,#0f172a_46%,#020617_100%)] text-slate-50">
      <section className="mx-auto flex max-w-[1500px] flex-col gap-6 px-4 py-5 sm:px-6 lg:flex-row lg:px-8 lg:py-8">
        <Sidebar view={view === "player" ? "players" : view === "team" ? "home" : view === "game" ? "games" : view} onChange={(next) => { setView(next); resetPaging(); }} seriesCode={seriesCode} />
        <div className="min-w-0 flex-1">
          <div className="mb-6 rounded-[28px] border border-white/8 bg-white/[0.03] px-5 py-4 text-sm leading-6 text-slate-300 shadow-[0_20px_80px_rgba(2,6,23,0.28)]">
            <span className="font-semibold text-white">DB snapshot</span> 기준 데이터입니다. 현재는 PostgreSQL에 적재된 실제 2025 시즌 실데이터를 기준으로 시리즈별 집계를 보여줍니다.
            <div className="mt-2 text-xs text-slate-400">{buildFreshnessLabel(activeFreshness)}</div>
          </div>
          {isLoading ? <div className="rounded-[28px] border border-white/10 bg-white/4 px-6 py-10 text-slate-300">시즌 데이터를 불러오는 중입니다...</div> : null}
          {!isLoading && error ? <div className="rounded-[28px] border border-rose-300/20 bg-rose-300/10 px-6 py-10 text-rose-100">{error}</div> : null}
          {!isLoading && !error && snapshot && season !== null && view === "home" ? <HomeView season={season} seasons={seasons} seriesCode={seriesCode} onSeasonChange={handleSeasonChange} onSeriesChange={handleSeriesChange} snapshot={snapshot} onSelectTeam={handleSelectTeam} /> : null}
          {!isLoading && !error && snapshot && season !== null && view === "players" ? <PlayersView season={season} seasons={seasons} seriesCode={seriesCode} onSeasonChange={handleSeasonChange} onSeriesChange={handleSeriesChange} snapshot={snapshot} mode={mode} onModeChange={(nextMode) => { setMode(nextMode); resetPaging(); }} qualifiedHittersOnly={qualifiedHittersOnly} onQualifiedHittersOnlyChange={(next) => { setQualifiedHittersOnly(next); resetPaging(); }} qualifiedPitchersOnly={qualifiedPitchersOnly} onQualifiedPitchersOnlyChange={(next) => { setQualifiedPitchersOnly(next); resetPaging(); }} playerGroup={playerGroup} onPlayerGroupChange={(group) => { setPlayerGroup(group); resetPaging(); }} page={page} pageSize={pageSize} onPageChange={setPage} onPageSizeChange={(size) => { setPageSize(size); resetPaging(); }} selectedCategoryKey={selectedCategoryKey} onSelectedCategoryKeyChange={(key) => { setSelectedCategoryKey(key); resetPaging(); }} onSelectPlayer={handleSelectPlayer} /> : null}
          {!isLoading && !error && playerDetail && season !== null && view === "player" ? <PlayerDetailView season={season} seasons={seasons} seriesCode={seriesCode} onSeasonChange={handleSeasonChange} onSeriesChange={handleSeriesChange} detail={playerDetail} onBack={() => { setView("players"); resetPaging(); }} onPageChange={setPage} onPageSizeChange={(size) => { setPageSize(size); resetPaging(); }} onOpenGame={handleOpenGame} /> : null}
          {!isLoading && !error && teamDetail && season !== null && view === "team" ? <TeamDetailView season={season} seasons={seasons} seriesCode={seriesCode} onSeasonChange={handleSeasonChange} onSeriesChange={handleSeriesChange} detail={teamDetail} onOpenGame={handleOpenGame} /> : null}
          {!isLoading && !error && gamesPage && season !== null && view === "games" ? <GamesView season={season} seasons={seasons} seriesCode={seriesCode} onSeasonChange={handleSeasonChange} onSeriesChange={handleSeriesChange} gamesPage={gamesPage} onPageChange={setPage} onPageSizeChange={(size) => { setPageSize(size); resetPaging(); }} onOpenGame={handleOpenGame} /> : null}
          {!isLoading && !error && gameDetail && view === "game" ? <GameDetailView game={gameDetail} onBack={() => { setView("games"); resetPaging(); }} /> : null}
        </div>
      </section>
    </main>
  );
}
