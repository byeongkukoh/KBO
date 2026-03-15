import { useMemo, useState } from "react";
import { CartesianGrid, Legend, Line, LineChart, PolarAngleAxis, PolarGrid, PolarRadiusAxis, Radar, RadarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { comparePlayers } from "../../../lib/api";
import type { PlayerComparison, PlayerGroup, LeaderboardPlayer, SeriesCode } from "../../../types/records";

type Props = {
  season: number;
  seriesCode: SeriesCode;
  group: PlayerGroup;
  candidates: LeaderboardPlayer[];
};

const hitterRadarKeys = ["battingAvg", "ops", "iso", "woba", "wrcPlus", "stolenBases"];
const pitcherRadarKeys = ["era", "whip", "kPer9", "bbPer9", "kbb", "fip"];

export function PlayerComparisonPanel({ season, seriesCode, group, candidates }: Props) {
  const [left, setLeft] = useState<string>(candidates[0]?.playerId ?? "");
  const [right, setRight] = useState<string>(candidates[1]?.playerId ?? candidates[0]?.playerId ?? "");
  const [comparison, setComparison] = useState<PlayerComparison | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [monthlyKey, setMonthlyKey] = useState(group === "hitters" ? "battingAvg" : "era");

  const options = useMemo(() => candidates.map((player) => ({ value: player.playerId, label: `${player.playerName} (${player.teamCode})` })), [candidates]);

  const radarKeys = group === "hitters" ? hitterRadarKeys : pitcherRadarKeys;
  const radarData = useMemo(() => {
    if (!comparison || comparison.players.length < 2) return [];
    const [a, b] = comparison.players;
    return radarKeys.map((key) => ({
      metric: key,
      [a.playerName]: a.metrics[key] ?? 0,
      [b.playerName]: b.metrics[key] ?? 0,
    }));
  }, [comparison, radarKeys]);

  const lineData = useMemo(() => {
    if (!comparison || comparison.players.length < 2) return [];
    const [a, b] = comparison.players;
    return a.monthlySplits.map((split, index) => ({
      monthLabel: split.monthLabel,
      [a.playerName]: split[monthlyKey as keyof typeof split] ?? null,
      [b.playerName]: b.monthlySplits[index]?.[monthlyKey as keyof typeof split] ?? null,
    }));
  }, [comparison, monthlyKey]);

  async function loadComparison() {
    setLoading(true);
    setError(null);
    try {
      const next = await comparePlayers({ playerKeys: [left, right], season, seriesCode, group });
      setComparison(next);
    } catch (caughtError) {
      setComparison(null);
      setError(caughtError instanceof Error ? caughtError.message : "선수 비교 데이터를 불러오지 못했습니다.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="space-y-4 rounded-[28px] border border-white/10 bg-slate-950/60 p-5">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <h3 className="text-xl font-semibold text-white">선수 비교</h3>
          <p className="mt-1 text-sm text-slate-400">두 선수를 골라 스파이더 차트와 월별 추이를 비교합니다.</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <select className="rounded-full border border-white/10 bg-white/5 px-3 py-2 text-white" value={left} onChange={(event) => setLeft(event.target.value)}>
            {options.map((option) => <option key={option.value} value={option.value} className="bg-slate-900 text-white">{option.label}</option>)}
          </select>
          <select className="rounded-full border border-white/10 bg-white/5 px-3 py-2 text-white" value={right} onChange={(event) => setRight(event.target.value)}>
            {options.map((option) => <option key={option.value} value={option.value} className="bg-slate-900 text-white">{option.label}</option>)}
          </select>
          <button type="button" className="rounded-full border border-cyan-300/35 bg-cyan-300/12 px-4 py-2 text-white" onClick={() => void loadComparison()}>비교하기</button>
        </div>
      </div>

      {loading ? <div className="rounded-2xl border border-white/10 bg-white/4 px-4 py-6 text-slate-300">선수 비교 데이터를 불러오는 중입니다...</div> : null}
      {!loading && error ? <div className="rounded-2xl border border-rose-300/20 bg-rose-300/10 px-4 py-6 text-rose-100">{error}</div> : null}
      {!loading && comparison && comparison.players.length === 2 ? (
        <div className="grid gap-4 xl:grid-cols-2">
          <div className="h-[360px] rounded-2xl border border-white/10 bg-slate-900/70 p-4">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={radarData}>
                <PolarGrid />
                <PolarAngleAxis dataKey="metric" />
                <PolarRadiusAxis />
                <Radar name={comparison.players[0].playerName} dataKey={comparison.players[0].playerName} stroke="#38bdf8" fill="#38bdf8" fillOpacity={0.25} />
                <Radar name={comparison.players[1].playerName} dataKey={comparison.players[1].playerName} stroke="#f59e0b" fill="#f59e0b" fillOpacity={0.18} />
                <Legend />
                <Tooltip />
              </RadarChart>
            </ResponsiveContainer>
          </div>
          <div className="rounded-2xl border border-white/10 bg-slate-900/70 p-4">
            <div className="mb-3 flex flex-wrap gap-2">
              {(group === "hitters"
                ? ["battingAvg", "ops", "hits", "homeRuns", "stolenBases", "woba", "wrcPlus"]
                : ["era", "whip", "strikeouts", "wins", "fip", "kPer9"]
              ).map((key) => (
                <button key={key} type="button" className={`rounded-full border px-3 py-2 text-sm ${monthlyKey === key ? "border-cyan-300/35 bg-cyan-300/12 text-white" : "border-white/10 bg-white/5 text-slate-300"}`} onClick={() => setMonthlyKey(key)}>
                  {key}
                </button>
              ))}
            </div>
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={lineData}>
                  <CartesianGrid stroke="rgba(148,163,184,0.12)" strokeDasharray="3 3" />
                  <XAxis dataKey="monthLabel" stroke="rgba(148,163,184,0.8)" />
                  <YAxis stroke="rgba(148,163,184,0.8)" />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey={comparison.players[0].playerName} stroke="#38bdf8" strokeWidth={3} />
                  <Line type="monotone" dataKey={comparison.players[1].playerName} stroke="#f59e0b" strokeWidth={3} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      ) : null}
    </section>
  );
}
