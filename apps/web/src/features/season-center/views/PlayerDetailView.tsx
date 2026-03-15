import type { PlayerDetail, PlayerGroup, SeriesCode } from "../../../types/records";
import { PaginationControls } from "../components/PaginationControls";
import { SeasonSelect } from "../components/SeasonSelect";
import { SeriesSelect } from "../components/SeriesSelect";

export function PlayerDetailView({ season, seasons, seriesCode, onSeasonChange, onSeriesChange, detail, onBack, onPageChange, onPageSizeChange }: { season: number; seasons: number[]; seriesCode: SeriesCode; onSeasonChange: (season: number) => void; onSeriesChange: (series: SeriesCode) => void; detail: PlayerDetail; onBack: () => void; onPageChange: (page: number) => void; onPageSizeChange: (pageSize: number) => void }) {
  const isHitter = detail.group === "hitters";

  return (
    <section className="space-y-8">
      <div className="rounded-[32px] border border-white/10 bg-[radial-gradient(circle_at_top_left,rgba(56,189,248,0.14),transparent_22%),linear-gradient(180deg,rgba(15,23,42,0.96),rgba(2,6,23,0.94))] p-6 shadow-[0_30px_90px_rgba(8,47,73,0.35)] lg:p-8">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <span className="inline-flex rounded-full border border-cyan-300/20 bg-cyan-300/10 px-3 py-1 text-xs uppercase tracking-[0.28em] text-cyan-100/80">Player / Detail</span>
            <h2 className="mt-4 text-3xl font-semibold tracking-tight text-white sm:text-4xl">{detail.playerName}</h2>
            <p className="mt-2 text-sm text-cyan-100/70">{detail.teamCode} · {isHitter ? "타자" : "투수"} · {detail.qualified ? "규정 기록 충족" : "규정 기록 미충족"}</p>
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <SeasonSelect seasons={seasons} value={season} onChange={onSeasonChange} />
            <SeriesSelect value={seriesCode} onChange={onSeriesChange} />
            <button type="button" className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-white" onClick={onBack}>선수 기록으로 돌아가기</button>
          </div>
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-4">
        {Object.entries(detail.metrics).map(([key, value]) => (
          <article key={key} className="rounded-2xl border border-white/10 bg-slate-950/60 p-4">
            <div className="text-xs uppercase tracking-[0.2em] text-slate-400">{key}</div>
            <div className="mt-2 text-2xl font-semibold text-white">{value === null ? "-" : typeof value === "number" ? value.toFixed(3).replace(/\.000$/, "") : value}</div>
          </article>
        ))}
      </div>

      <div className="overflow-hidden rounded-[28px] border border-white/10 bg-slate-950/60">
        <div className="border-b border-white/10 px-5 py-5">
          <h3 className="text-xl font-semibold text-white">시즌 경기별 기록</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm text-slate-200">
            <thead className="bg-white/6 text-xs uppercase tracking-[0.18em] text-slate-400">
              <tr>
                <th className="px-4 py-3 text-left">날짜</th>
                <th className="px-4 py-3 text-left">상대</th>
                <th className="px-4 py-3 text-left">결과</th>
                <th className="px-4 py-3 text-left">구장</th>
                {isHitter ? (
                  <>
                    <th className="px-4 py-3 text-right">PA</th>
                    <th className="px-4 py-3 text-right">AB</th>
                    <th className="px-4 py-3 text-right">H</th>
                    <th className="px-4 py-3 text-right">2B</th>
                    <th className="px-4 py-3 text-right">HR</th>
                    <th className="px-4 py-3 text-right">SB</th>
                    <th className="px-4 py-3 text-right">RBI</th>
                  </>
                ) : (
                  <>
                    <th className="px-4 py-3 text-right">IP</th>
                    <th className="px-4 py-3 text-right">H</th>
                    <th className="px-4 py-3 text-right">BB</th>
                    <th className="px-4 py-3 text-right">SO</th>
                    <th className="px-4 py-3 text-right">ER</th>
                    <th className="px-4 py-3 text-right">결정</th>
                  </>
                )}
              </tr>
            </thead>
            <tbody>
              {detail.logs.map((log) => (
                <tr key={`${log.gameId}-${log.gameDate}`} className="border-t border-white/8">
                  <td className="px-4 py-4">{log.gameDate}</td>
                  <td className="px-4 py-4">{log.opponentTeamCode}</td>
                  <td className="px-4 py-4">{log.result}</td>
                  <td className="px-4 py-4">{log.stadium}</td>
                  {isHitter ? (
                    <>
                      <td className="px-4 py-4 text-right">{log.plateAppearances ?? "-"}</td>
                      <td className="px-4 py-4 text-right">{log.atBats ?? "-"}</td>
                      <td className="px-4 py-4 text-right">{log.hits ?? "-"}</td>
                      <td className="px-4 py-4 text-right">{log.doubles ?? "-"}</td>
                      <td className="px-4 py-4 text-right">{log.homeRuns ?? "-"}</td>
                      <td className="px-4 py-4 text-right">{log.stolenBases ?? "-"}</td>
                      <td className="px-4 py-4 text-right">{log.runsBattedIn ?? "-"}</td>
                    </>
                  ) : (
                    <>
                      <td className="px-4 py-4 text-right">{log.inningsDisplay ?? "-"}</td>
                      <td className="px-4 py-4 text-right">{log.hitsAllowed ?? "-"}</td>
                      <td className="px-4 py-4 text-right">{log.walksAllowed ?? "-"}</td>
                      <td className="px-4 py-4 text-right">{log.strikeouts ?? "-"}</td>
                      <td className="px-4 py-4 text-right">{log.earnedRuns ?? "-"}</td>
                      <td className="px-4 py-4 text-right">{log.decisionCode ?? "-"}</td>
                    </>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <PaginationControls page={detail.page} pageSize={detail.pageSize} totalCount={detail.totalCount} totalPages={detail.totalPages} onChange={onPageChange} onPageSizeChange={onPageSizeChange} />
      </div>
    </section>
  );
}
