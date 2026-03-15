import type { SeriesCode, TeamSeasonDetail } from "../../../types/records";
import { SeasonSelect } from "../components/SeasonSelect";
import { SeriesSelect } from "../components/SeriesSelect";

export function TeamDetailView({ season, seasons, seriesCode, onSeasonChange, onSeriesChange, detail, onOpenGame }: { season: number; seasons: number[]; seriesCode: SeriesCode; onSeasonChange: (season: number) => void; onSeriesChange: (series: SeriesCode) => void; detail: TeamSeasonDetail; onOpenGame: (gameId: string) => void }) {
  return (
    <section className="space-y-8">
      <div className="rounded-[32px] border border-white/10 bg-[radial-gradient(circle_at_top_left,rgba(34,197,94,0.14),transparent_22%),linear-gradient(180deg,rgba(15,23,42,0.96),rgba(2,6,23,0.94))] p-6 shadow-[0_30px_90px_rgba(22,101,52,0.28)] lg:p-8">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <span className="inline-flex rounded-full border border-emerald-300/20 bg-emerald-300/10 px-3 py-1 text-xs uppercase tracking-[0.28em] text-emerald-100/80">Teams / Detail</span>
            <h2 className="mt-4 text-3xl font-semibold tracking-tight text-white sm:text-4xl">{detail.teamName}</h2>
            <p className="mt-2 text-sm text-emerald-100/70">{detail.teamCode} · {detail.wins}-{detail.losses}-{detail.draws}</p>
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <SeasonSelect seasons={seasons} value={season} onChange={onSeasonChange} />
            <SeriesSelect value={seriesCode} onChange={onSeriesChange} />
          </div>
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-4">
        {[
          ["승률", detail.winPct?.toFixed(3) ?? "-"],
          ["OPS+", detail.opsPlus?.toFixed(1) ?? "-"],
          ["ERA+", detail.eraPlus?.toFixed(1) ?? "-"],
          ["최근 10경기", detail.lastTen],
        ].map(([label, value]) => (
          <article key={label} className="rounded-2xl border border-white/10 bg-slate-950/60 p-4">
            <div className="text-xs uppercase tracking-[0.2em] text-slate-400">{label}</div>
            <div className="mt-2 text-2xl font-semibold text-white">{value}</div>
          </article>
        ))}
      </div>

      <div className="overflow-hidden rounded-[28px] border border-white/10 bg-slate-950/60">
        <div className="border-b border-white/10 px-5 py-5">
          <h3 className="text-xl font-semibold text-white">최근 경기</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm text-slate-200">
            <thead className="bg-white/6 text-xs uppercase tracking-[0.18em] text-slate-400">
              <tr>
                <th className="px-4 py-3 text-left">날짜</th>
                <th className="px-4 py-3 text-left">상대</th>
                <th className="px-4 py-3 text-left">결과</th>
                <th className="px-4 py-3 text-left">구장</th>
                <th className="px-4 py-3 text-right">점수</th>
              </tr>
            </thead>
            <tbody>
              {detail.recentGames.map((game) => (
                <tr key={game.gameId} className="border-t border-white/8">
                  <td className="px-4 py-4">{game.gameDate}</td>
                  <td className="px-4 py-4">{game.opponentTeamCode}</td>
                  <td className="px-4 py-4">{game.result}</td>
                  <td className="px-4 py-4">{game.stadium}</td>
                  <td className="px-4 py-4 text-right"><button type="button" className="hover:text-cyan-200" onClick={() => onOpenGame(game.gameId)}>{game.teamScore}-{game.opponentScore}</button></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}
