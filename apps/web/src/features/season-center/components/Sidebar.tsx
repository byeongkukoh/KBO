import type { AppView, SeriesCode } from "../../../types/records";
import { seriesOptions } from "./SeriesSelect";

export function Sidebar({ view, onChange, seriesCode }: { view: AppView; onChange: (view: AppView) => void; seriesCode: SeriesCode }) {
  const seriesLabel = seriesOptions.find((item) => item.key === seriesCode)?.label ?? "정규시즌";

  return (
    <aside className="flex w-full flex-col justify-between rounded-[28px] border border-white/10 bg-[linear-gradient(180deg,rgba(15,23,42,0.96),rgba(2,6,23,0.92))] p-5 shadow-[0_30px_90px_rgba(2,6,23,0.55)] lg:w-72">
      <div>
        <div className="rounded-2xl border border-cyan-300/15 bg-cyan-300/10 p-4">
          <p className="text-xs uppercase tracking-[0.28em] text-cyan-100/70">KBO Record</p>
          <h1 className="mt-3 text-2xl font-semibold text-white">Season Center</h1>
          <p className="mt-3 text-sm leading-6 text-slate-300">시즌과 시리즈 구분을 기준으로 팀 순위와 선수 기록을 실제 DB snapshot 응답에서 탐색합니다.</p>
        </div>

        <nav className="mt-8 grid gap-2">
          {[
            { key: "home" as const, label: "홈", description: "팀 순위와 팀 통계" },
            { key: "players" as const, label: "선수 기록", description: "Top 5와 전체 기록" },
          ].map((item) => {
            const active = view === item.key;
            return (
              <button
                key={item.key}
                type="button"
                className={`rounded-2xl border px-4 py-4 text-left transition ${active ? "border-cyan-300/30 bg-cyan-300/12 text-white" : "border-white/8 bg-white/4 text-slate-300 hover:border-white/14 hover:bg-white/7"}`}
                onClick={() => onChange(item.key)}
              >
                <div className="text-base font-semibold">{item.label}</div>
                <div className="mt-1 text-sm text-slate-400">{item.description}</div>
              </button>
            );
          })}
        </nav>
      </div>

      <div className="mt-8 rounded-2xl border border-emerald-300/15 bg-emerald-300/8 p-4 text-sm text-emerald-50/85">
        <div className="text-xs uppercase tracking-[0.24em] text-emerald-100/65">Data Mode</div>
        <div className="mt-2 font-semibold">DB Snapshot / {seriesLabel}</div>
        <div className="mt-2 leading-6">현재 화면은 PostgreSQL에 적재된 실제 2025 시즌 snapshot 응답을 기준으로 동작합니다.</div>
      </div>
    </aside>
  );
}
