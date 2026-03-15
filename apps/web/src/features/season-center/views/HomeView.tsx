import { useMemo, useState } from "react";

import { sortStandings, type TeamSortKey } from "../../../lib/records";
import type { SeasonSnapshot, SeriesCode } from "../../../types/records";
import { SeasonSelect } from "../components/SeasonSelect";
import { SeriesSelect } from "../components/SeriesSelect";

const teamSortOptions: Array<{ key: TeamSortKey; label: string }> = [
  { key: "winPct", label: "승률" },
  { key: "hits", label: "안타" },
  { key: "doubles", label: "2루타" },
  { key: "battingAvg", label: "타율" },
  { key: "ops", label: "OPS" },
  { key: "era", label: "평균자책점" },
];

export function HomeView({ season, seasons, seriesCode, onSeasonChange, onSeriesChange, snapshot, onSelectTeam, emptyMessage }: { season: number; seasons: number[]; seriesCode: SeriesCode; onSeasonChange: (season: number) => void; onSeriesChange: (series: SeriesCode) => void; snapshot: SeasonSnapshot | null; onSelectTeam: (teamCode: string) => void; emptyMessage?: string | null }) {
  const [sortKey, setSortKey] = useState<TeamSortKey>("winPct");
  const sortedStandings = useMemo(() => sortStandings(snapshot?.standings ?? [], sortKey), [snapshot?.standings, sortKey]);
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
            <div className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-slate-300">{snapshot?.snapshotLabel ?? "데이터 없음"}</div>
          </div>
        </div>

        {emptyMessage ? (
          <div className="rounded-[24px] border border-dashed border-white/15 bg-slate-950/35 px-6 py-8 text-sm text-slate-300">
            {emptyMessage}
          </div>
        ) : (
        <div className="grid gap-4 lg:grid-cols-3">
          {podium.map((team, index) => (
            <article key={team.teamCode} className="rounded-[24px] border border-white/10 bg-slate-950/35 p-5 backdrop-blur">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="text-xs uppercase tracking-[0.24em] text-slate-400">#{index + 1}</p>
                  <button type="button" className="mt-2 text-2xl font-semibold text-white hover:text-cyan-200" onClick={() => onSelectTeam(team.teamCode)}>{team.teamName}</button>
                  <p className="mt-2 text-sm text-cyan-100/75">{team.teamCode} · 승률 {team.winPct.toFixed(3)}</p>
                </div>
                <div className="rounded-2xl border border-cyan-300/20 bg-cyan-300/10 px-4 py-3 text-right">
                  <div className="text-xs text-cyan-100/70">Games Back</div>
                  <div className="mt-1 text-lg font-semibold text-white">{team.gamesBack === 0 ? "-" : team.gamesBack.toFixed(1)}</div>
                </div>
              </div>
              <dl className="mt-5 grid grid-cols-3 gap-3 text-sm text-slate-200">
                <div className="rounded-2xl border border-white/8 bg-white/4 p-3"><dt className="text-slate-400">승-패-무</dt><dd className="mt-1 font-semibold text-white">{team.wins}-{team.losses}-{team.draws}</dd></div>
                <div className="rounded-2xl border border-white/8 bg-white/4 p-3"><dt className="text-slate-400">최근 10경기</dt><dd className="mt-1 font-semibold text-white">{team.lastTen}</dd></div>
                <div className="rounded-2xl border border-white/8 bg-white/4 p-3"><dt className="text-slate-400">연속</dt><dd className="mt-1 font-semibold text-white">{team.streak}</dd></div>
              </dl>
            </article>
          ))}
        </div>
        )}
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
        {!emptyMessage ? <div className="overflow-x-auto">
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
                  <td className="px-4 py-4"><button type="button" className="font-medium text-white hover:text-cyan-200" onClick={() => onSelectTeam(team.teamCode)}>{team.teamName}</button><div className="text-xs text-slate-400">{team.wins}-{team.losses}-{team.draws}</div></td>
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
        </div> : <div className="px-5 py-8 text-sm text-slate-400">다른 시즌 또는 시리즈를 선택해보세요.</div>}
      </div>
    </section>
  );
}
