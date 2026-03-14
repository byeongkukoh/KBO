import { useEffect, useMemo, useState } from "react";

import { GameVerificationPanel } from "./components/GameVerificationPanel";
import { getGameDetail, getPlayerSummary } from "./lib/api";
import type { GameDetail, PlayerSummary } from "./types/game";

const defaultGameId = "20260314WONC0";
const defaultPlayerKey = "wo-안치홍";

function App() {
  const [gameId, setGameId] = useState(defaultGameId);
  const [playerKey, setPlayerKey] = useState(defaultPlayerKey);
  const [game, setGame] = useState<GameDetail | null>(null);
  const [summary, setSummary] = useState<PlayerSummary | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [reloadToken, setReloadToken] = useState(0);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setIsLoading(true);
      setError(null);

      try {
        const [nextGame, nextSummary] = await Promise.all([getGameDetail(gameId), getPlayerSummary(playerKey)]);

        if (cancelled) {
          return;
        }

        setGame(nextGame);
        setSummary(nextSummary);
      } catch (caughtError) {
        if (cancelled) {
          return;
        }

        const message = caughtError instanceof Error ? caughtError.message : "알 수 없는 오류가 발생했습니다.";
        setGame(null);
        setSummary(null);
        setError(message);
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    }

    void load();

    return () => {
      cancelled = true;
    };
  }, [gameId, playerKey, reloadToken]);

  const helperText = useMemo(
    () =>
      "fixture 또는 ingest된 실제 게임을 기준으로 PostgreSQL 적재 결과와 파생 통계를 한 화면에서 확인합니다.",
    [],
  );

  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top,rgba(34,211,238,0.18),transparent_28%),linear-gradient(180deg,#020617_0%,#0f172a_52%,#020617_100%)] text-slate-50">
      <section className="mx-auto max-w-7xl px-6 py-12 sm:px-8 lg:px-10 lg:py-16">
        <div className="flex flex-col gap-10">
          <header className="grid gap-6 lg:grid-cols-[1.35fr_0.85fr] lg:items-end">
            <div>
              <span className="inline-flex w-fit rounded-full border border-cyan-300/25 bg-cyan-300/10 px-4 py-1 text-xs uppercase tracking-[0.28em] text-cyan-100">
                KBO Vertical Slice
              </span>
              <h1 className="mt-5 max-w-4xl text-4xl font-semibold tracking-tight text-white sm:text-5xl lg:text-6xl">
                raw 게임 데이터에서 파생 선수 통계까지 이어지는 검증 화면
              </h1>
              <p className="mt-5 max-w-3xl text-base leading-7 text-slate-300 sm:text-lg">{helperText}</p>
            </div>

            <form
              className="rounded-[28px] border border-white/10 bg-slate-950/55 p-6 shadow-[0_30px_90px_rgba(15,23,42,0.42)] backdrop-blur"
              onSubmit={(event) => {
                event.preventDefault();
                setReloadToken((current) => current + 1);
              }}
            >
              <div className="grid gap-4">
                <label className="grid gap-2 text-sm text-slate-300">
                  <span className="uppercase tracking-[0.18em] text-slate-400">Game ID</span>
                  <input
                    className="rounded-2xl border border-white/10 bg-slate-900 px-4 py-3 text-white outline-none transition focus:border-cyan-300/50"
                    value={gameId}
                    onChange={(event) => setGameId(event.target.value)}
                    placeholder="20260314WONC0"
                  />
                </label>
                <label className="grid gap-2 text-sm text-slate-300">
                  <span className="uppercase tracking-[0.18em] text-slate-400">Player Key</span>
                  <input
                    className="rounded-2xl border border-white/10 bg-slate-900 px-4 py-3 text-white outline-none transition focus:border-cyan-300/50"
                    value={playerKey}
                    onChange={(event) => setPlayerKey(event.target.value)}
                    placeholder="wo-안치홍"
                  />
                </label>
                <button
                  type="submit"
                  className="mt-2 rounded-2xl bg-cyan-300 px-4 py-3 font-semibold text-slate-950 transition hover:bg-cyan-200"
                >
                  검증 데이터 다시 불러오기
                </button>
              </div>
            </form>
          </header>

          {isLoading ? (
            <section className="grid gap-4 lg:grid-cols-3">
              {Array.from({ length: 3 }).map((_, index) => (
                <div
                  key={index}
                  className="h-52 animate-pulse rounded-[28px] border border-white/8 bg-white/5"
                />
              ))}
            </section>
          ) : null}

          {!isLoading && error ? (
            <section className="rounded-[28px] border border-rose-300/20 bg-rose-400/10 p-6 text-rose-100">
              <p className="text-xs uppercase tracking-[0.24em] text-rose-200/70">Fetch Error</p>
              <h2 className="mt-3 text-2xl font-semibold">데이터를 불러오지 못했습니다.</h2>
              <p className="mt-3 whitespace-pre-wrap text-sm leading-6 text-rose-100/85">{error}</p>
            </section>
          ) : null}

          {!isLoading && !error && game && summary ? <GameVerificationPanel game={game} summary={summary} /> : null}
        </div>
      </section>
    </main>
  );
}

export default App;
