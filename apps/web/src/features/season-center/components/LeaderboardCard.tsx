import type { LeaderboardCategory, LeaderboardPlayer } from "../../../types/records";

export function LeaderboardCard({ rows, category, onSelectPlayer }: { rows: LeaderboardPlayer[]; category: LeaderboardCategory; onSelectPlayer: (playerId: string, group: "hitters" | "pitchers") => void }) {
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
                  <button type="button" className="font-medium text-white hover:text-cyan-200" onClick={() => onSelectPlayer(player.playerId, category.playerType === "hitter" ? "hitters" : "pitchers")}>{player.playerName}</button>
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
