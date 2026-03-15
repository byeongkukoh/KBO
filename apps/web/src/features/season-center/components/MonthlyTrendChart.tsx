import { CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import type { PlayerGroup, PlayerMonthlySplit } from "../../../types/records";

type MonthlyTrendChartProps = {
  group: PlayerGroup;
  splits: PlayerMonthlySplit[];
  statKey: string;
  onStatKeyChange: (key: string) => void;
};

const hitterOptions = [
  { key: "battingAvg", label: "타율" },
  { key: "ops", label: "OPS" },
  { key: "hits", label: "안타" },
  { key: "homeRuns", label: "홈런" },
  { key: "stolenBases", label: "도루" },
  { key: "woba", label: "wOBA" },
  { key: "wrcPlus", label: "wRC+" },
];

const pitcherOptions = [
  { key: "era", label: "ERA" },
  { key: "whip", label: "WHIP" },
  { key: "strikeouts", label: "탈삼진" },
  { key: "wins", label: "승리" },
  { key: "fip", label: "FIP" },
  { key: "kPer9", label: "K/9" },
];

export function MonthlyTrendChart({ group, splits, statKey, onStatKeyChange }: MonthlyTrendChartProps) {
  const options = group === "hitters" ? hitterOptions : pitcherOptions;
  const chartData = splits.map((split) => ({
    monthLabel: split.monthLabel,
    games: split.games,
    value: split[statKey as keyof PlayerMonthlySplit] ?? null,
  }));

  return (
    <section className="overflow-hidden rounded-[28px] border border-white/10 bg-slate-950/60">
      <div className="flex flex-col gap-4 border-b border-white/10 px-5 py-5 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <h3 className="text-xl font-semibold text-white">월별 추이</h3>
          <p className="mt-1 text-sm text-slate-400">월별 지표 흐름을 그래프로 확인합니다.</p>
        </div>
        <div className="flex flex-wrap gap-2">
          {options.map((option) => (
            <button
              key={option.key}
              type="button"
              className={`rounded-full border px-3 py-2 text-sm transition ${statKey === option.key ? "border-cyan-300/35 bg-cyan-300/12 text-white" : "border-white/10 bg-white/5 text-slate-300"}`}
              onClick={() => onStatKeyChange(option.key)}
            >
              {option.label}
            </button>
          ))}
        </div>
      </div>
      <div className="h-[340px] px-3 py-4 sm:px-6">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData}>
            <CartesianGrid stroke="rgba(148,163,184,0.12)" strokeDasharray="3 3" />
            <XAxis dataKey="monthLabel" stroke="rgba(148,163,184,0.8)" />
            <YAxis stroke="rgba(148,163,184,0.8)" />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="value" name={options.find((item) => item.key === statKey)?.label ?? statKey} stroke="#38bdf8" strokeWidth={3} dot={{ r: 4 }} connectNulls={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}
