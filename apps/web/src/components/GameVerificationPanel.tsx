import type { BattingRow, GameDetail, PitchingRow, PlayerSummary, TeamStat } from "../types/game";

type GameVerificationPanelProps = {
  game: GameDetail;
  summary: PlayerSummary;
};

function formatMetric(value: number | null | undefined): string {
  if (value === null || value === undefined) {
    return "-";
  }

  return value.toFixed(3);
}

function formatOutsToInnings(outs: number): string {
  const whole = Math.floor(outs / 3);
  const remainder = outs % 3;

  if (remainder === 0) {
    return `${whole}`;
  }

  return `${whole}.${remainder}`;
}

function TeamStatCard({ stat }: { stat: TeamStat }) {
  return (
    <article className="rounded-2xl border border-white/10 bg-slate-900/70 p-5 shadow-[0_20px_60px_rgba(15,23,42,0.35)]">
      <div className="flex items-center justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.24em] text-cyan-200/70">Team Totals</p>
          <h3 className="mt-2 text-xl font-semibold text-white">{stat.team_name}</h3>
        </div>
        <div className="rounded-full border border-cyan-300/20 bg-cyan-300/10 px-3 py-1 text-sm text-cyan-100">
          {stat.team_code}
        </div>
      </div>
      <dl className="mt-5 grid grid-cols-2 gap-3 text-sm text-slate-200 sm:grid-cols-4">
        <div className="rounded-xl border border-white/8 bg-white/4 p-3">
          <dt className="text-slate-400">R</dt>
          <dd className="mt-1 text-lg font-semibold text-white">{stat.runs}</dd>
        </div>
        <div className="rounded-xl border border-white/8 bg-white/4 p-3">
          <dt className="text-slate-400">H</dt>
          <dd className="mt-1 text-lg font-semibold text-white">{stat.hits}</dd>
        </div>
        <div className="rounded-xl border border-white/8 bg-white/4 p-3">
          <dt className="text-slate-400">E</dt>
          <dd className="mt-1 text-lg font-semibold text-white">{stat.errors}</dd>
        </div>
        <div className="rounded-xl border border-white/8 bg-white/4 p-3">
          <dt className="text-slate-400">BB</dt>
          <dd className="mt-1 text-lg font-semibold text-white">{stat.walks}</dd>
        </div>
      </dl>
    </article>
  );
}

function BattingTable({ rows }: { rows: BattingRow[] }) {
  return (
    <div className="overflow-hidden rounded-2xl border border-white/10 bg-slate-900/70">
      <div className="border-b border-white/10 px-5 py-4">
        <h3 className="text-lg font-semibold text-white">Batting Rows</h3>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full text-sm text-slate-200">
          <thead className="bg-white/6 text-xs uppercase tracking-[0.2em] text-slate-400">
            <tr>
              <th className="px-4 py-3 text-left">Player</th>
              <th className="px-4 py-3 text-left">Team</th>
              <th className="px-4 py-3 text-right">AB</th>
              <th className="px-4 py-3 text-right">H</th>
              <th className="px-4 py-3 text-right">2B</th>
              <th className="px-4 py-3 text-right">3B</th>
              <th className="px-4 py-3 text-right">HR</th>
              <th className="px-4 py-3 text-right">BB</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={`${row.player_key}-${row.team_code}`} className="border-t border-white/8">
                <td className="px-4 py-3 font-medium text-white">{row.player_name}</td>
                <td className="px-4 py-3">{row.team_code}</td>
                <td className="px-4 py-3 text-right">{row.at_bats}</td>
                <td className="px-4 py-3 text-right">{row.hits}</td>
                <td className="px-4 py-3 text-right">{row.doubles}</td>
                <td className="px-4 py-3 text-right">{row.triples}</td>
                <td className="px-4 py-3 text-right">{row.home_runs}</td>
                <td className="px-4 py-3 text-right">{row.walks}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function PitchingTable({ rows }: { rows: PitchingRow[] }) {
  return (
    <div className="overflow-hidden rounded-2xl border border-white/10 bg-slate-900/70">
      <div className="border-b border-white/10 px-5 py-4">
        <h3 className="text-lg font-semibold text-white">Pitching Rows</h3>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full text-sm text-slate-200">
          <thead className="bg-white/6 text-xs uppercase tracking-[0.2em] text-slate-400">
            <tr>
              <th className="px-4 py-3 text-left">Player</th>
              <th className="px-4 py-3 text-left">Team</th>
              <th className="px-4 py-3 text-right">IP</th>
              <th className="px-4 py-3 text-right">H</th>
              <th className="px-4 py-3 text-right">BB</th>
              <th className="px-4 py-3 text-right">SO</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={`${row.player_key}-${row.team_code}`} className="border-t border-white/8">
                <td className="px-4 py-3 font-medium text-white">{row.player_name}</td>
                <td className="px-4 py-3">{row.team_code}</td>
                <td className="px-4 py-3 text-right">{formatOutsToInnings(row.innings_outs)}</td>
                <td className="px-4 py-3 text-right">{row.hits_allowed}</td>
                <td className="px-4 py-3 text-right">{row.walks_allowed}</td>
                <td className="px-4 py-3 text-right">{row.strikeouts}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export function GameVerificationPanel({ game, summary }: GameVerificationPanelProps) {
  return (
    <section className="space-y-8">
      <div className="grid gap-4 lg:grid-cols-[1.4fr_0.9fr]">
        <article className="overflow-hidden rounded-[28px] border border-cyan-300/15 bg-[linear-gradient(135deg,rgba(8,145,178,0.18),rgba(15,23,42,0.92))] p-6 shadow-[0_24px_80px_rgba(14,116,144,0.25)]">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <p className="text-xs uppercase tracking-[0.32em] text-cyan-100/75">Fixture Verification</p>
              <h2 className="mt-3 text-3xl font-semibold tracking-tight text-white sm:text-4xl">
                {game.away_team_code} {game.away_score} - {game.home_score} {game.home_team_code}
              </h2>
              <p className="mt-3 max-w-2xl text-sm leading-6 text-cyan-50/80">
                한 경기 fixture에서 파생 통계까지 실제 API 응답을 검증하는 수직 슬라이스입니다.
              </p>
            </div>
            <div className="rounded-2xl border border-white/12 bg-slate-950/35 px-4 py-3 text-right text-sm text-slate-100 backdrop-blur">
              <div className="text-slate-300">Game ID</div>
              <div className="mt-1 font-semibold text-white" data-testid="game-id">
                {game.game_id}
              </div>
            </div>
          </div>

          <dl className="mt-8 grid gap-3 text-sm text-slate-100 sm:grid-cols-3 xl:grid-cols-5">
            <div className="rounded-2xl border border-white/10 bg-slate-950/30 p-4 backdrop-blur">
              <dt className="text-slate-300">Date</dt>
              <dd className="mt-1 font-medium text-white">{game.game_date}</dd>
            </div>
            <div className="rounded-2xl border border-white/10 bg-slate-950/30 p-4 backdrop-blur">
              <dt className="text-slate-300">Status</dt>
              <dd className="mt-1 font-medium text-white">{game.status_code}</dd>
            </div>
            <div className="rounded-2xl border border-white/10 bg-slate-950/30 p-4 backdrop-blur">
              <dt className="text-slate-300">Stadium</dt>
              <dd className="mt-1 font-medium text-white">{game.stadium}</dd>
            </div>
            <div className="rounded-2xl border border-white/10 bg-slate-950/30 p-4 backdrop-blur">
              <dt className="text-slate-300">Away</dt>
              <dd className="mt-1 font-medium text-white">{game.away_team_code}</dd>
            </div>
            <div className="rounded-2xl border border-white/10 bg-slate-950/30 p-4 backdrop-blur">
              <dt className="text-slate-300">Home</dt>
              <dd className="mt-1 font-medium text-white">{game.home_team_code}</dd>
            </div>
          </dl>
        </article>

        <article className="rounded-[28px] border border-amber-300/15 bg-[linear-gradient(160deg,rgba(120,53,15,0.28),rgba(15,23,42,0.92))] p-6 shadow-[0_24px_80px_rgba(120,53,15,0.18)]">
          <p className="text-xs uppercase tracking-[0.32em] text-amber-100/70">Derived Player Summary</p>
          <h2 className="mt-3 text-2xl font-semibold text-white">{summary.player_name}</h2>
          <p className="mt-1 text-sm text-amber-50/80">{summary.player_key}</p>
          <dl className="mt-6 grid grid-cols-2 gap-3 text-sm text-slate-100">
            <div className="rounded-2xl border border-white/10 bg-slate-950/35 p-4">
              <dt className="text-slate-400">Games</dt>
              <dd className="mt-1 text-xl font-semibold text-white">{summary.games_count}</dd>
            </div>
            <div className="rounded-2xl border border-white/10 bg-slate-950/35 p-4">
              <dt className="text-slate-400">OPS</dt>
              <dd className="mt-1 text-xl font-semibold text-white" data-testid={`player-${summary.player_key}-ops`}>
                {formatMetric(summary.batting_metrics.ops)}
              </dd>
            </div>
            <div className="rounded-2xl border border-white/10 bg-slate-950/35 p-4">
              <dt className="text-slate-400">AVG</dt>
              <dd className="mt-1 text-xl font-semibold text-white">{formatMetric(summary.batting_metrics.avg)}</dd>
            </div>
            <div className="rounded-2xl border border-white/10 bg-slate-950/35 p-4">
              <dt className="text-slate-400">WHIP</dt>
              <dd className="mt-1 text-xl font-semibold text-white">{formatMetric(summary.pitching_metrics.whip)}</dd>
            </div>
          </dl>
        </article>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        {game.team_stats.map((stat) => (
          <TeamStatCard key={stat.team_code} stat={stat} />
        ))}
      </div>

      <div className="overflow-hidden rounded-2xl border border-white/10 bg-slate-900/70">
        <div className="border-b border-white/10 px-5 py-4">
          <h3 className="text-lg font-semibold text-white">Inning Lines</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm text-slate-200">
            <thead className="bg-white/6 text-xs uppercase tracking-[0.2em] text-slate-400">
              <tr>
                <th className="px-4 py-3 text-left">Team</th>
                {game.innings.map((inning) => (
                  <th key={inning.inning_no} className="px-4 py-3 text-right">
                    {inning.inning_no}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              <tr className="border-t border-white/8">
                <td className="px-4 py-3 font-medium text-white">{game.away_team_code}</td>
                {game.innings.map((inning) => (
                  <td key={`away-${inning.inning_no}`} className="px-4 py-3 text-right">
                    {inning.away_runs}
                  </td>
                ))}
              </tr>
              <tr className="border-t border-white/8">
                <td className="px-4 py-3 font-medium text-white">{game.home_team_code}</td>
                {game.innings.map((inning) => (
                  <td key={`home-${inning.inning_no}`} className="px-4 py-3 text-right">
                    {inning.home_runs}
                  </td>
                ))}
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <BattingTable rows={game.batting_rows} />
        <PitchingTable rows={game.pitching_rows} />
      </div>
    </section>
  );
}
