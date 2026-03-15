import type { GameListPage, SeriesCode } from "../../../types/records";
import { PaginationControls } from "../components/PaginationControls";
import { SeasonSelect } from "../components/SeasonSelect";
import { SeriesSelect } from "../components/SeriesSelect";

export function GamesView({ season, seasons, seriesCode, onSeasonChange, onSeriesChange, gamesPage, onPageChange, onPageSizeChange, onOpenGame }: { season: number; seasons: number[]; seriesCode: SeriesCode; onSeasonChange: (season: number) => void; onSeriesChange: (series: SeriesCode) => void; gamesPage: GameListPage; onPageChange: (page: number) => void; onPageSizeChange: (pageSize: number) => void; onOpenGame: (gameId: string) => void }) {
  return (
    <section className="space-y-8">
      <div className="rounded-[32px] border border-white/10 bg-[radial-gradient(circle_at_top_left,rgba(251,191,36,0.14),transparent_22%),linear-gradient(180deg,rgba(15,23,42,0.96),rgba(2,6,23,0.94))] p-6 shadow-[0_30px_90px_rgba(120,53,15,0.28)] lg:p-8">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <span className="inline-flex rounded-full border border-amber-300/20 bg-amber-300/10 px-3 py-1 text-xs uppercase tracking-[0.28em] text-amber-100/80">Games / Browse</span>
            <h2 className="mt-4 text-3xl font-semibold tracking-tight text-white sm:text-4xl">{season} 시즌 경기 기록</h2>
            <p className="mt-3 max-w-3xl text-sm leading-7 text-slate-300">완료된 경기 목록을 시리즈 기준으로 탐색하고, 경기 상세로 이동할 수 있습니다.</p>
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <SeasonSelect seasons={seasons} value={season} onChange={onSeasonChange} />
            <SeriesSelect value={seriesCode} onChange={onSeriesChange} />
          </div>
        </div>
      </div>

      <section className="overflow-hidden rounded-[28px] border border-white/10 bg-slate-950/60">
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm text-slate-200">
            <thead className="bg-white/6 text-xs uppercase tracking-[0.18em] text-slate-400">
              <tr>
                <th className="px-4 py-3 text-left">날짜</th>
                <th className="px-4 py-3 text-left">시리즈</th>
                <th className="px-4 py-3 text-left">원정</th>
                <th className="px-4 py-3 text-left">홈</th>
                <th className="px-4 py-3 text-left">구장</th>
                <th className="px-4 py-3 text-right">스코어</th>
              </tr>
            </thead>
            <tbody>
              {gamesPage.items.map((game) => (
                <tr key={game.gameId} className="border-t border-white/8">
                  <td className="px-4 py-4">{game.gameDate}</td>
                  <td className="px-4 py-4">{game.seriesName}</td>
                  <td className="px-4 py-4">{game.awayTeamCode}</td>
                  <td className="px-4 py-4">{game.homeTeamCode}</td>
                  <td className="px-4 py-4">{game.stadium}</td>
                  <td className="px-4 py-4 text-right"><button type="button" className="hover:text-cyan-200" onClick={() => onOpenGame(game.gameId)}>{game.awayScore}-{game.homeScore}</button></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <PaginationControls page={gamesPage.page} pageSize={gamesPage.pageSize} totalCount={gamesPage.totalCount} totalPages={gamesPage.totalPages} onChange={onPageChange} onPageSizeChange={onPageSizeChange} />
      </section>
    </section>
  );
}
