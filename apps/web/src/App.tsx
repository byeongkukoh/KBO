import { useEffect, useMemo, useState } from "react";

import { getSeasonSnapshot as fetchSeasonSnapshot, getSeasons } from "./lib/api";
import { getLeaderboardCategories, sortPlayers, sortStandings, type FullViewMode, type PlayerGroup, type TeamSortKey } from "./lib/records";
import type { AppView, LeaderboardCategory, SeasonSnapshot, SeriesCode } from "./types/records";

const currentYear = new Date().getFullYear();
const teamSortOptions: Array<{ key: TeamSortKey; label: string }> = [
  { key: "winPct", label: "승률" },
  { key: "hits", label: "안타" },
  { key: "doubles", label: "2루타" },
  { key: "battingAvg", label: "타율" },
  { key: "ops", label: "OPS" },
  { key: "era", label: "평균자책점" },
];
const seriesOptions: Array<{ key: SeriesCode; label: string }> = [
  { key: "preseason", label: "프리시즌" },
  { key: "regular", label: "정규시즌" },
  { key: "postseason", label: "포스트시즌" },
];

function selectDefaultSeason(seasons: number[]): number | null {
  if (seasons.length === 0) {
    return null;
  }
  if (seasons.includes(currentYear)) {
    return currentYear;
  }
  return seasons[0];
}

function SeasonSelect({ seasons, value, onChange }: { seasons: number[]; value: number; onChange: (value: number) => void }) {
  return (
    <label className="flex items-center gap-3 rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-slate-200">
      <span className="text-slate-400">시즌</span>
      <select className="bg-transparent font-medium text-white outline-none" value={value} onChange={(event) => onChange(Number(event.target.value))}>
        {seasons.map((season) => (
          <option key={season} value={season} className="bg-slate-900 text-white">
            {season}
          </option>
        ))}
      </select>
    </label>
  );
}

function SeriesSelect({ value, onChange }: { value: SeriesCode; onChange: (value: SeriesCode) => void }) {
  return (
    <div className="flex flex-wrap gap-2">
      {seriesOptions.map((option) => (
        <button
          key={option.key}
          type="button"
          className={`rounded-full border px-3 py-2 text-sm transition ${value === option.key ? "border-cyan-300/35 bg-cyan-300/12 text-white" : "border-white/10 bg-white/5 text-slate-300 hover:border-white/20 hover:bg-white/8"}`}
          onClick={() => onChange(option.key)}
        >
          {option.label}
        </button>
      ))}
    </div>
  );
}

function Sidebar({ view, onChange, seriesCode }: { view: AppView; onChange: (view: AppView) => void; seriesCode: SeriesCode }) {
  const seriesLabel = seriesOptions.find((item) => item.key === seriesCode)?.label ?? "정규시즌";

  return (
    <aside className="flex w-full flex-col justify-between rounded-[28px] border border-white/10 bg-[linear-gradient(180deg,rgba(15,23,42,0.96),rgba(2,6,23,0.92))] p-5 shadow-[0_30px_90px_rgba(2,6,23,0.55)] lg:w-72">
      <div>
        <div className="rounded-2xl border border-cyan-300/15 bg-cyan-300/10 p-4">
          <p className="text-xs uppercase tracking-[0.28em] text-cyan-100/70">KBO Record</p>
          <h1 className="mt-3 text-2xl font-semibold text-white">Season Center</h1>
          <p className="mt-3 text-sm leading-6 text-slate-300">시즌과 시리즈 구분을 기준으로 팀 순위와 선수 기록을 실제 DB snapshot 응답에서 탐색합니다.</p>
        </div>

        <nav className="mt-8 grid gap-2">
          {[
            { key: "home" as const, label: "홈", description: "팀 순위와 팀 통계" },
            { key: "players" as const, label: "선수 기록", description: "Top 5와 전체 기록" },
          ].map((item) => {
            const active = view === item.key;
            return (
              <button
                key={item.key}
                type="button"
                className={`rounded-2xl border px-4 py-4 text-left transition ${active ? "border-cyan-300/30 bg-cyan-300/12 text-white" : "border-white/8 bg-white/4 text-slate-300 hover:border-white/14 hover:bg-white/7"}`}
                onClick={() => onChange(item.key)}
              >
                <div className="text-base font-semibold">{item.label}</div>
                <div className="mt-1 text-sm text-slate-400">{item.description}</div>
              </button>
            );
          })}
        </nav>
      </div>

      <div className="mt-8 rounded-2xl border border-emerald-300/15 bg-emerald-300/8 p-4 text-sm text-emerald-50/85">
        <div className="text-xs uppercase tracking-[0.24em] text-emerald-100/65">Data Mode</div>
        <div className="mt-2 font-semibold">DB Snapshot / {seriesLabel}</div>
        <div className="mt-2 leading-6">현재 화면은 PostgreSQL에 적재된 실제 2025 시즌 snapshot 응답을 기준으로 동작합니다.</div>
      </div>
    </aside>
  );
}

function HomeView({ season, seasons, seriesCode, onSeasonChange, onSeriesChange, snapshot }: { season: number; seasons: number[]; seriesCode: SeriesCode; onSeasonChange: (season: number) => void; onSeriesChange: (series: SeriesCode) => void; snapshot: SeasonSnapshot }) {
  const [sortKey, setSortKey] = useState<TeamSortKey>("winPct");
  const sortedStandings = useMemo(() => sortStandings(snapshot.standings, sortKey), [snapshot.standings, sortKey]);
  const podium = sortedStandings.slice(0, 3);

  return (
    <section className="space-y-8">
      <div className="flex flex-col gap-4 rounded-[32px] border border-white/10 bg-[radial-gradient(circle_at_top_left,rgba(56,189,248,0.16),transparent_28%),linear-gradient(180deg,rgba(15,23,42,0.96),rgba(2,6,23,0.94))] p-6 shadow-[0_30px_90px_rgba(8,47,73,0.35)] lg:p-8">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <span className="inline-flex rounded-full border border-cyan-300/20 bg-cyan-300/10 px-3 py-1 text-xs uppercase tracking-[0.28em] text-cyan-100/80">Home / Standings</span>
            <h2 className="mt-4 text-3xl font-semibold tracking-tight text-white sm:text-4xl">{season} 시즌 팀 순위</h2>
            <p className="mt-3 max-w-3xl text-sm leading-7 text-slate-300">현재 시리즈 구분에 맞춰 실제 적재 데이터를 집계한 순위와 팀 통계를 보여줍니다.</p>
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <SeasonSelect seasons={seasons} value={season} onChange={onSeasonChange} />
            <SeriesSelect value={seriesCode} onChange={onSeriesChange} />
            <div className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-slate-300">{snapshot.snapshotLabel}</div>
          </div>
        </div>

        <div className="grid gap-4 lg:grid-cols-3">
          {podium.map((team, index) => (
            <article key={team.teamCode} className="rounded-[24px] border border-white/10 bg-slate-950/35 p-5 backdrop-blur">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="text-xs uppercase tracking-[0.24em] text-slate-400">#{index + 1}</p>
                  <h3 className="mt-2 text-2xl font-semibold text-white">{team.teamName}</h3>
                  <p className="mt-2 text-sm text-cyan-100/75">{team.teamCode} · 승률 {team.winPct.toFixed(3)}</p>
                </div>
                <div className="rounded-2xl border border-cyan-300/20 bg-cyan-300/10 px-4 py-3 text-right">
                  <div className="text-xs text-cyan-100/70">Games Back</div>
                  <div className="mt-1 text-lg font-semibold text-white">{team.gamesBack === 0 ? "-" : team.gamesBack.toFixed(1)}</div>
                </div>
              </div>
              <dl className="mt-5 grid grid-cols-3 gap-3 text-sm text-slate-200">
                <div className="rounded-2xl border border-white/8 bg-white/4 p-3">
                  <dt className="text-slate-400">승-패-무</dt>
                  <dd className="mt-1 font-semibold text-white">{team.wins}-{team.losses}-{team.draws}</dd>
                </div>
                <div className="rounded-2xl border border-white/8 bg-white/4 p-3">
                  <dt className="text-slate-400">최근 10경기</dt>
                  <dd className="mt-1 font-semibold text-white">{team.lastTen}</dd>
                </div>
                <div className="rounded-2xl border border-white/8 bg-white/4 p-3">
                  <dt className="text-slate-400">연속</dt>
                  <dd className="mt-1 font-semibold text-white">{team.streak}</dd>
                </div>
              </dl>
            </article>
          ))}
        </div>
      </div>

      <div className="overflow-hidden rounded-[28px] border border-white/10 bg-slate-950/60">
        <div className="flex flex-col gap-4 border-b border-white/10 px-5 py-5 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <h3 className="text-xl font-semibold text-white">팀별 시즌 통계</h3>
            <p className="mt-1 text-sm text-slate-400">기본 정렬은 승률이며, 컬럼 버튼으로 시즌 통계 기준을 바로 바꿀 수 있습니다.</p>
          </div>
          <div className="flex flex-wrap gap-2">
            {teamSortOptions.map((option) => (
              <button key={option.key} type="button" className={`rounded-full border px-3 py-2 text-sm transition ${sortKey === option.key ? "border-cyan-300/35 bg-cyan-300/12 text-white" : "border-white/10 bg-white/5 text-slate-300 hover:border-white/15 hover:bg-white/8"}`} onClick={() => setSortKey(option.key)}>
                {option.label}
              </button>
            ))}
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm text-slate-200">
            <thead className="bg-white/6 text-xs uppercase tracking-[0.18em] text-slate-400">
              <tr>
                <th className="px-4 py-3 text-left">순위</th>
                <th className="px-4 py-3 text-left">팀</th>
                <th className="px-4 py-3 text-right">승률</th>
                <th className="px-4 py-3 text-right">안타</th>
                <th className="px-4 py-3 text-right">2루타</th>
                <th className="px-4 py-3 text-right">도루</th>
                <th className="px-4 py-3 text-right">타율</th>
                <th className="px-4 py-3 text-right">OPS</th>
                <th className="px-4 py-3 text-right">ERA</th>
                <th className="px-4 py-3 text-right">득실차</th>
              </tr>
            </thead>
            <tbody>
              {sortedStandings.map((team) => (
                <tr key={team.teamCode} className="border-t border-white/8">
                  <td className="px-4 py-4 text-left font-semibold text-white">{team.rank}</td>
                  <td className="px-4 py-4"><div className="font-medium text-white">{team.teamName}</div><div className="text-xs text-slate-400">{team.wins}-{team.losses}-{team.draws}</div></td>
                  <td className="px-4 py-4 text-right">{team.winPct.toFixed(3)}</td>
                  <td className="px-4 py-4 text-right">{team.hits}</td>
                  <td className="px-4 py-4 text-right">{team.doubles}</td>
                  <td className="px-4 py-4 text-right">{team.stolenBases}</td>
                  <td className="px-4 py-4 text-right">{team.battingAvg.toFixed(3)}</td>
                  <td className="px-4 py-4 text-right">{team.ops.toFixed(3)}</td>
                  <td className="px-4 py-4 text-right">{team.era.toFixed(2)}</td>
                  <td className={`px-4 py-4 text-right ${team.runDiff >= 0 ? "text-cyan-200" : "text-rose-200"}`}>{team.runDiff > 0 ? `+${team.runDiff}` : team.runDiff}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}

function LeaderboardCard({ snapshot, category, qualifiedOnly }: { snapshot: SeasonSnapshot; category: LeaderboardCategory; qualifiedOnly: boolean }) {
  const group: PlayerGroup = category.playerType === "hitter" ? "hitters" : "pitchers";
  const rows = sortPlayers(
    snapshot.players
      .filter((player) => (group === "hitters" ? player.battingAvg !== undefined : player.era !== undefined))
      .filter((player) => (group === "hitters" ? (qualifiedOnly ? player.qualifiedHitter : true) : qualifiedOnly ? player.qualifiedPitcher : true)),
    category,
  ).slice(0, 5);

  return (
    <article className="rounded-[24px] border border-white/10 bg-slate-950/60 p-5">
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="text-xs uppercase tracking-[0.24em] text-slate-400">{category.playerType === "hitter" ? "Hitter" : "Pitcher"}</p>
          <h3 className="mt-2 text-xl font-semibold text-white">{category.label}</h3>
        </div>
        <div className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-slate-300">Top 5</div>
      </div>
      <div className="mt-4 space-y-2">
        {rows.map((player, index) => {
          const value = player[category.statKey] as number | undefined;
          return (
            <div key={`${category.key}-${player.playerId}`} className="flex items-center justify-between rounded-2xl border border-white/8 bg-white/4 px-4 py-3">
              <div className="flex items-center gap-3">
                <div className="flex h-9 w-9 items-center justify-center rounded-full bg-cyan-300/12 text-sm font-semibold text-cyan-100">{index + 1}</div>
                <div>
                  <div className="font-medium text-white">{player.playerName}</div>
                  <div className="text-xs text-slate-400">{player.teamCode}</div>
                </div>
              </div>
              <div className="text-right font-semibold text-white">{value === undefined ? "-" : category.precision ? value.toFixed(category.precision) : value}</div>
            </div>
          );
        })}
      </div>
    </article>
  );
}

function PlayersView({ season, seasons, seriesCode, onSeasonChange, onSeriesChange, snapshot }: { season: number; seasons: number[]; seriesCode: SeriesCode; onSeasonChange: (season: number) => void; onSeriesChange: (series: SeriesCode) => void; snapshot: SeasonSnapshot }) {
  const [mode, setMode] = useState<FullViewMode>("top5");
  const [qualifiedHittersOnly, setQualifiedHittersOnly] = useState(true);
  const [qualifiedPitchersOnly, setQualifiedPitchersOnly] = useState(true);
  const [playerGroup, setPlayerGroup] = useState<PlayerGroup>("hitters");
  const hitterCategories = getLeaderboardCategories("hitters");
  const pitcherCategories = getLeaderboardCategories("pitchers");
  const fullCategories = getLeaderboardCategories(playerGroup);
  const [selectedCategoryKey, setSelectedCategoryKey] = useState<string>(fullCategories[0].key);
  const selectedCategory = fullCategories.find((category) => category.key === selectedCategoryKey) ?? fullCategories[0];

  useEffect(() => {
    setSelectedCategoryKey(getLeaderboardCategories(playerGroup)[0].key);
  }, [playerGroup]);

  const fullRows = useMemo(() => {
    const groupRows = snapshot.players.filter((player) => (playerGroup === "hitters" ? player.battingAvg !== undefined : player.era !== undefined));
    const filtered = groupRows.filter((player) =>
      playerGroup === "hitters" ? (qualifiedHittersOnly ? player.qualifiedHitter : true) : qualifiedPitchersOnly ? player.qualifiedPitcher : true,
    );
    return sortPlayers(filtered, selectedCategory);
  }, [playerGroup, qualifiedHittersOnly, qualifiedPitchersOnly, selectedCategory, snapshot.players]);

  return (
    <section className="space-y-8">
      <div className="rounded-[32px] border border-white/10 bg-[radial-gradient(circle_at_top_right,rgba(251,191,36,0.16),transparent_26%),linear-gradient(180deg,rgba(15,23,42,0.96),rgba(2,6,23,0.94))] p-6 shadow-[0_30px_90px_rgba(120,53,15,0.3)] lg:p-8">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <span className="inline-flex rounded-full border border-amber-300/20 bg-amber-300/10 px-3 py-1 text-xs uppercase tracking-[0.28em] text-amber-100/80">Players / Leaderboards</span>
            <h2 className="mt-4 text-3xl font-semibold tracking-tight text-white sm:text-4xl">{season} 시즌 선수 기록</h2>
            <p className="mt-3 max-w-3xl text-sm leading-7 text-slate-300">실제 적재된 시즌 snapshot 기준 Top 5와 전체 기록표를 탐색합니다.</p>
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <SeasonSelect seasons={seasons} value={season} onChange={onSeasonChange} />
            <SeriesSelect value={seriesCode} onChange={onSeriesChange} />
            <button type="button" className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-white transition hover:border-white/20 hover:bg-white/8" onClick={() => setMode((current) => (current === "top5" ? "full" : "top5"))}>
              {mode === "top5" ? "전체 보기" : "Top 5 보기"}
            </button>
            <div className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-slate-300">{snapshot.snapshotLabel}</div>
          </div>
        </div>
      </div>

      {mode === "top5" ? (
        <div className="space-y-8">
          <section>
            <div className="mb-4 flex items-center justify-between gap-4">
              <h3 className="text-2xl font-semibold text-white">타자 Top 5</h3>
              <button type="button" className={`rounded-full border px-4 py-2 text-sm transition ${qualifiedHittersOnly ? "border-cyan-300/30 bg-cyan-300/12 text-white" : "border-white/10 bg-white/5 text-slate-300"}`} onClick={() => setQualifiedHittersOnly((current) => !current)}>
                {qualifiedHittersOnly ? "정규타석만 보기" : "전체 타자 보기"}
              </button>
            </div>
            <div className="grid gap-4 xl:grid-cols-2">
              {hitterCategories.map((category) => (
                <LeaderboardCard key={category.key} snapshot={snapshot} category={category} qualifiedOnly={qualifiedHittersOnly} />
              ))}
            </div>
          </section>
          <section>
            <div className="mb-4 flex items-center justify-between gap-4">
              <h3 className="text-2xl font-semibold text-white">투수 Top 5</h3>
              <button type="button" className={`rounded-full border px-4 py-2 text-sm transition ${qualifiedPitchersOnly ? "border-amber-300/30 bg-amber-300/12 text-white" : "border-white/10 bg-white/5 text-slate-300"}`} onClick={() => setQualifiedPitchersOnly((current) => !current)}>
                {qualifiedPitchersOnly ? "정규이닝만 보기" : "전체 투수 보기"}
              </button>
            </div>
            <div className="grid gap-4 xl:grid-cols-2">
              {pitcherCategories.map((category) => (
                <LeaderboardCard key={category.key} snapshot={snapshot} category={category} qualifiedOnly={qualifiedPitchersOnly} />
              ))}
            </div>
          </section>
        </div>
      ) : (
        <section className="overflow-hidden rounded-[28px] border border-white/10 bg-slate-950/60">
          <div className="flex flex-col gap-4 border-b border-white/10 px-5 py-5 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <h3 className="text-xl font-semibold text-white">전체 선수 기록</h3>
              <p className="mt-1 text-sm text-slate-400">기록 부문을 누르면 해당 컬럼 기준으로 전체 테이블이 정렬됩니다.</p>
            </div>
            <div className="flex flex-wrap gap-2">
              <button type="button" className={`rounded-full border px-3 py-2 text-sm transition ${playerGroup === "hitters" ? "border-cyan-300/35 bg-cyan-300/12 text-white" : "border-white/10 bg-white/5 text-slate-300"}`} onClick={() => setPlayerGroup("hitters")}>타자</button>
              <button type="button" className={`rounded-full border px-3 py-2 text-sm transition ${playerGroup === "pitchers" ? "border-amber-300/35 bg-amber-300/12 text-white" : "border-white/10 bg-white/5 text-slate-300"}`} onClick={() => setPlayerGroup("pitchers")}>투수</button>
              {fullCategories.map((category) => (
                <button key={category.key} type="button" className={`rounded-full border px-3 py-2 text-sm transition ${selectedCategory.key === category.key ? "border-white/20 bg-white/10 text-white" : "border-white/10 bg-white/5 text-slate-300"}`} onClick={() => setSelectedCategoryKey(category.key)}>
                  {category.label}
                </button>
              ))}
              <button
                type="button"
                className={`rounded-full border px-3 py-2 text-sm transition ${playerGroup === "hitters" ? (qualifiedHittersOnly ? "border-cyan-300/35 bg-cyan-300/12 text-white" : "border-white/10 bg-white/5 text-slate-300") : qualifiedPitchersOnly ? "border-amber-300/35 bg-amber-300/12 text-white" : "border-white/10 bg-white/5 text-slate-300"}`}
                onClick={() => {
                  if (playerGroup === "hitters") {
                    setQualifiedHittersOnly((current) => !current);
                    return;
                  }
                  setQualifiedPitchersOnly((current) => !current);
                }}
              >
                {playerGroup === "hitters" ? (qualifiedHittersOnly ? "정규타석만" : "전체 타자") : qualifiedPitchersOnly ? "정규이닝만" : "전체 투수"}
              </button>
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm text-slate-200">
              <thead className="bg-white/6 text-xs uppercase tracking-[0.18em] text-slate-400">
                <tr>
                  <th className="px-4 py-3 text-left">순위</th>
                  <th className="px-4 py-3 text-left">선수</th>
                  <th className="px-4 py-3 text-left">팀</th>
                  <th className="px-4 py-3 text-right">경기</th>
                  {playerGroup === "hitters" ? (
                    <>
                      <th className="px-4 py-3 text-right">타율</th>
                      <th className="px-4 py-3 text-right">안타</th>
                      <th className="px-4 py-3 text-right">2루타</th>
                      <th className="px-4 py-3 text-right">홈런</th>
                      <th className="px-4 py-3 text-right">도루</th>
                      <th className="px-4 py-3 text-right">OPS</th>
                    </>
                  ) : (
                    <>
                      <th className="px-4 py-3 text-right">이닝</th>
                      <th className="px-4 py-3 text-right">ERA</th>
                      <th className="px-4 py-3 text-right">탈삼진</th>
                      <th className="px-4 py-3 text-right">승리</th>
                      <th className="px-4 py-3 text-right">WHIP</th>
                    </>
                  )}
                </tr>
              </thead>
              <tbody>
                {fullRows.map((player, index) => (
                  <tr key={player.playerId} className="border-t border-white/8">
                    <td className="px-4 py-4 font-semibold text-white">{index + 1}</td>
                    <td className="px-4 py-4 font-medium text-white">{player.playerName}</td>
                    <td className="px-4 py-4">{player.teamCode}</td>
                    <td className="px-4 py-4 text-right">{player.games}</td>
                    {playerGroup === "hitters" ? (
                      <>
                        <td className="px-4 py-4 text-right">{player.battingAvg?.toFixed(3) ?? "-"}</td>
                        <td className="px-4 py-4 text-right">{player.hits ?? "-"}</td>
                        <td className="px-4 py-4 text-right">{player.doubles ?? "-"}</td>
                        <td className="px-4 py-4 text-right">{player.homeRuns ?? "-"}</td>
                        <td className="px-4 py-4 text-right">{player.stolenBases ?? "-"}</td>
                        <td className="px-4 py-4 text-right">{player.ops?.toFixed(3) ?? "-"}</td>
                      </>
                    ) : (
                      <>
                        <td className="px-4 py-4 text-right">{player.innings?.toFixed(1) ?? "-"}</td>
                        <td className="px-4 py-4 text-right">{player.era?.toFixed(2) ?? "-"}</td>
                        <td className="px-4 py-4 text-right">{player.strikeouts ?? "-"}</td>
                        <td className="px-4 py-4 text-right">{player.wins ?? "-"}</td>
                        <td className="px-4 py-4 text-right">{player.whip?.toFixed(2) ?? "-"}</td>
                      </>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}
    </section>
  );
}

function App() {
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
            <span className="font-semibold text-white">DB snapshot</span> 기준 데이터입니다. 현재는 PostgreSQL에 적재된 2025 시즌 실데이터를 기준으로 시리즈별 집계를 보여줍니다.
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

export default App;
