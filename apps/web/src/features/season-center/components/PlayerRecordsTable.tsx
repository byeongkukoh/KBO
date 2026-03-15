import type { PlayerGroup, PlayerRecordRow } from "../../../types/records";
import { PaginationControls } from "./PaginationControls";

export function PlayerRecordsTable({ group, rows, page, pageSize, totalCount, totalPages, onPageChange, onPageSizeChange, onSelectPlayer }: { group: PlayerGroup; rows: PlayerRecordRow[]; page: number; pageSize: number; totalCount: number; totalPages: number; onPageChange: (page: number) => void; onPageSizeChange: (pageSize: number) => void; onSelectPlayer: (playerId: string, group: PlayerGroup) => void }) {
  return (
    <section className="overflow-hidden rounded-[28px] border border-white/10 bg-slate-950/60">
      <div className="overflow-x-auto">
        <table className="min-w-full text-sm text-slate-200">
          <thead className="bg-white/6 text-xs uppercase tracking-[0.18em] text-slate-400">
            <tr>
              <th className="px-4 py-3 text-left">순위</th>
              <th className="px-4 py-3 text-left">선수</th>
              <th className="px-4 py-3 text-left">팀</th>
              <th className="px-4 py-3 text-right">경기</th>
              {group === "hitters" ? (
                <>
                  <th className="px-4 py-3 text-right">타율</th>
                  <th className="px-4 py-3 text-right">안타</th>
                  <th className="px-4 py-3 text-right">2루타</th>
                  <th className="px-4 py-3 text-right">홈런</th>
                  <th className="px-4 py-3 text-right">도루</th>
                  <th className="px-4 py-3 text-right">ISO</th>
                  <th className="px-4 py-3 text-right">BABIP</th>
                  <th className="px-4 py-3 text-right">BB%</th>
                  <th className="px-4 py-3 text-right">K%</th>
                  <th className="px-4 py-3 text-right">OPS</th>
                </>
              ) : (
                <>
                  <th className="px-4 py-3 text-right">이닝</th>
                  <th className="px-4 py-3 text-right">ERA</th>
                  <th className="px-4 py-3 text-right">탈삼진</th>
                  <th className="px-4 py-3 text-right">승리</th>
                  <th className="px-4 py-3 text-right">WHIP</th>
                  <th className="px-4 py-3 text-right">K/9</th>
                  <th className="px-4 py-3 text-right">BB/9</th>
                  <th className="px-4 py-3 text-right">K/BB</th>
                </>
              )}
            </tr>
          </thead>
          <tbody>
            {rows.map((player) => (
              <tr key={player.playerId} className="border-t border-white/8">
                <td className="px-4 py-4 font-semibold text-white">{player.rank}</td>
                <td className="px-4 py-4 font-medium text-white"><button type="button" className="hover:text-cyan-200" onClick={() => onSelectPlayer(player.playerId, group)}>{player.playerName}</button></td>
                <td className="px-4 py-4">{player.teamCode}</td>
                <td className="px-4 py-4 text-right">{player.games}</td>
                {group === "hitters" ? (
                  <>
                    <td className="px-4 py-4 text-right">{player.battingAvg?.toFixed(3) ?? "-"}</td>
                    <td className="px-4 py-4 text-right">{player.hits ?? "-"}</td>
                    <td className="px-4 py-4 text-right">{player.doubles ?? "-"}</td>
                    <td className="px-4 py-4 text-right">{player.homeRuns ?? "-"}</td>
                    <td className="px-4 py-4 text-right">{player.stolenBases ?? "-"}</td>
                    <td className="px-4 py-4 text-right">{player.iso?.toFixed(3) ?? "-"}</td>
                    <td className="px-4 py-4 text-right">{player.babip?.toFixed(3) ?? "-"}</td>
                    <td className="px-4 py-4 text-right">{player.bbRate?.toFixed(3) ?? "-"}</td>
                    <td className="px-4 py-4 text-right">{player.kRate?.toFixed(3) ?? "-"}</td>
                    <td className="px-4 py-4 text-right">{player.ops?.toFixed(3) ?? "-"}</td>
                  </>
                ) : (
                  <>
                    <td className="px-4 py-4 text-right">{player.inningsDisplay ?? "-"}</td>
                    <td className="px-4 py-4 text-right">{player.era?.toFixed(2) ?? "-"}</td>
                    <td className="px-4 py-4 text-right">{player.strikeouts ?? "-"}</td>
                    <td className="px-4 py-4 text-right">{player.wins ?? "-"}</td>
                    <td className="px-4 py-4 text-right">{player.whip?.toFixed(2) ?? "-"}</td>
                    <td className="px-4 py-4 text-right">{player.kPer9?.toFixed(2) ?? "-"}</td>
                    <td className="px-4 py-4 text-right">{player.bbPer9?.toFixed(2) ?? "-"}</td>
                    <td className="px-4 py-4 text-right">{player.kbb?.toFixed(2) ?? "-"}</td>
                  </>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <PaginationControls page={page} pageSize={pageSize} totalCount={totalCount} totalPages={totalPages} onChange={onPageChange} onPageSizeChange={onPageSizeChange} />
    </section>
  );
}
