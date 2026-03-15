export function PaginationControls({ page, totalPages, onChange }: { page: number; totalPages: number; onChange: (page: number) => void }) {
  return (
    <div className="flex items-center justify-between gap-4 border-t border-white/10 px-5 py-4 text-sm text-slate-300">
      <div>
        페이지 {page} / {totalPages}
      </div>
      <div className="flex gap-2">
        <button type="button" className="rounded-full border border-white/10 bg-white/5 px-3 py-2 disabled:opacity-40" disabled={page <= 1} onClick={() => onChange(page - 1)}>
          이전
        </button>
        <button type="button" className="rounded-full border border-white/10 bg-white/5 px-3 py-2 disabled:opacity-40" disabled={page >= totalPages} onClick={() => onChange(page + 1)}>
          다음
        </button>
      </div>
    </div>
  );
}
