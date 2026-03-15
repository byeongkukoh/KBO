import type { SeriesCode } from "../../../types/records";

export const seriesOptions: Array<{ key: SeriesCode; label: string }> = [
  { key: "preseason", label: "프리시즌" },
  { key: "regular", label: "정규시즌" },
  { key: "postseason", label: "포스트시즌" },
];

export function SeriesSelect({ value, onChange }: { value: SeriesCode; onChange: (value: SeriesCode) => void }) {
  return (
    <div className="flex flex-wrap gap-2">
      {seriesOptions.map((option) => (
        <button
          key={option.key}
          type="button"
          className={`rounded-full border px-3 py-2 text-sm transition ${value === option.key ? "border-cyan-300/35 bg-cyan-300/12 text-white" : "border-white/10 bg-white/5 text-slate-300 hover:border-white/20 hover:bg-white/8"}`}
          onClick={() => onChange(option.key)}
        >
          {option.label}
        </button>
      ))}
    </div>
  );
}
