export function SeasonSelect({ seasons, value, onChange }: { seasons: number[]; value: number; onChange: (value: number) => void }) {
  return (
    <label className="flex items-center gap-3 rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-slate-200">
      <span className="text-slate-400">시즌</span>
      <select className="bg-transparent font-medium text-white outline-none" value={value} onChange={(event) => onChange(Number(event.target.value))}>
        {seasons.map((season) => (
          <option key={season} value={season} className="bg-slate-900 text-white">
            {season}
          </option>
        ))}
      </select>
    </label>
  );
}
