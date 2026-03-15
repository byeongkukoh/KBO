import type { GameDetail } from "../../../types/game";

function formatOutsToInnings(outs: number): string {
  const whole = Math.floor(outs / 3);
  const remainder = outs % 3;
  return remainder === 0 ? `${whole}` : `${whole}.${remainder}`;
}

export function GameDetailView({ game, onBack }: { game: GameDetail; onBack: () => void }) {
  return (
    <section className="space-y-8">
      <div className="rounded-[32px] border border-white/10 bg-[radial-gradient(circle_at_top_left,rgba(8,145,178,0.18),transparent_22%),linear-gradient(180deg,rgba(15,23,42,0.96),rgba(2,6,23,0.94))] p-6 shadow-[0_30px_90px_rgba(8,47,73,0.35)] lg:p-8">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <span className="inline-flex rounded-full border border-cyan-300/20 bg-cyan-300/10 px-3 py-1 text-xs uppercase tracking-[0.28em] text-cyan-100/80">Games / Detail</span>
            <h2 className="mt-4 text-3xl font-semibold tracking-tight text-white sm:text-4xl">{game.away_team_code} {game.away_score} - {game.home_score} {game.home_team_code}</h2>
            <p className="mt-3 text-sm text-slate-300">{game.game_date} · {game.stadium} · 경기 ID {game.game_id}</p>
          </div>
          <button type="button" className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-white" onClick={onBack}>경기 목록으로 돌아가기</button>
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        {game.team_stats.map((team) => (
          <article key={team.team_code} className="rounded-2xl border border-white/10 bg-slate-950/60 p-5">
            <h3 className="text-xl font-semibold text-white">{team.team_name}</h3>
            <dl className="mt-4 grid grid-cols-4 gap-3 text-sm text-slate-200">
              <div className="rounded-xl border border-white/8 bg-white/4 p-3"><dt className="text-slate-400">R</dt><dd className="mt-1 font-semibold text-white">{team.runs}</dd></div>
              <div className="rounded-xl border border-white/8 bg-white/4 p-3"><dt className="text-slate-400">H</dt><dd className="mt-1 font-semibold text-white">{team.hits}</dd></div>
              <div className="rounded-xl border border-white/8 bg-white/4 p-3"><dt className="text-slate-400">E</dt><dd className="mt-1 font-semibold text-white">{team.errors}</dd></div>
              <div className="rounded-xl border border-white/8 bg-white/4 p-3"><dt className="text-slate-400">BB</dt><dd className="mt-1 font-semibold text-white">{team.walks}</dd></div>
            </dl>
          </article>
        ))}
      </div>

      <div className="overflow-hidden rounded-[28px] border border-white/10 bg-slate-950/60">
        <div className="border-b border-white/10 px-5 py-4"><h3 className="text-lg font-semibold text-white">이닝별 점수</h3></div>
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm text-slate-200">
            <thead className="bg-white/6 text-xs uppercase tracking-[0.18em] text-slate-400"><tr><th className="px-4 py-3 text-left">팀</th>{game.innings.map((inning) => <th key={inning.inning_no} className="px-4 py-3 text-right">{inning.inning_no}</th>)}</tr></thead>
            <tbody>
              <tr className="border-t border-white/8"><td className="px-4 py-3 font-medium text-white">{game.away_team_code}</td>{game.innings.map((inning) => <td key={`away-${inning.inning_no}`} className="px-4 py-3 text-right">{inning.away_runs}</td>)}</tr>
              <tr className="border-t border-white/8"><td className="px-4 py-3 font-medium text-white">{game.home_team_code}</td>{game.innings.map((inning) => <td key={`home-${inning.inning_no}`} className="px-4 py-3 text-right">{inning.home_runs}</td>)}</tr>
            </tbody>
          </table>
        </div>
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <div className="overflow-hidden rounded-2xl border border-white/10 bg-slate-900/70">
          <div className="border-b border-white/10 px-5 py-4"><h3 className="text-lg font-semibold text-white">타자 기록</h3></div>
          <div className="overflow-x-auto"><table className="min-w-full text-sm text-slate-200"><thead className="bg-white/6 text-xs uppercase tracking-[0.18em] text-slate-400"><tr><th className="px-4 py-3 text-left">선수</th><th className="px-4 py-3 text-left">팀</th><th className="px-4 py-3 text-right">AB</th><th className="px-4 py-3 text-right">H</th><th className="px-4 py-3 text-right">2B</th><th className="px-4 py-3 text-right">HR</th></tr></thead><tbody>{game.batting_rows.map((row) => <tr key={`${row.player_key}-${row.team_code}`} className="border-t border-white/8"><td className="px-4 py-3 font-medium text-white">{row.player_name}</td><td className="px-4 py-3">{row.team_code}</td><td className="px-4 py-3 text-right">{row.at_bats}</td><td className="px-4 py-3 text-right">{row.hits}</td><td className="px-4 py-3 text-right">{row.doubles}</td><td className="px-4 py-3 text-right">{row.home_runs}</td></tr>)}</tbody></table></div>
        </div>
        <div className="overflow-hidden rounded-2xl border border-white/10 bg-slate-900/70">
          <div className="border-b border-white/10 px-5 py-4"><h3 className="text-lg font-semibold text-white">투수 기록</h3></div>
          <div className="overflow-x-auto"><table className="min-w-full text-sm text-slate-200"><thead className="bg-white/6 text-xs uppercase tracking-[0.18em] text-slate-400"><tr><th className="px-4 py-3 text-left">선수</th><th className="px-4 py-3 text-left">팀</th><th className="px-4 py-3 text-right">IP</th><th className="px-4 py-3 text-right">H</th><th className="px-4 py-3 text-right">BB</th><th className="px-4 py-3 text-right">SO</th></tr></thead><tbody>{game.pitching_rows.map((row) => <tr key={`${row.player_key}-${row.team_code}`} className="border-t border-white/8"><td className="px-4 py-3 font-medium text-white">{row.player_name}</td><td className="px-4 py-3">{row.team_code}</td><td className="px-4 py-3 text-right">{formatOutsToInnings(row.innings_outs)}</td><td className="px-4 py-3 text-right">{row.hits_allowed}</td><td className="px-4 py-3 text-right">{row.walks_allowed}</td><td className="px-4 py-3 text-right">{row.strikeouts}</td></tr>)}</tbody></table></div>
        </div>
      </div>
    </section>
  );
}
