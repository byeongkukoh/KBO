import { useEffect, useState } from "react";

export function PaginationControls({
  page,
  pageSize,
  totalCount,
  totalPages,
  onChange,
  onPageSizeChange,
}: {
  page: number;
  pageSize: number;
  totalCount: number;
  totalPages: number;
  onChange: (page: number) => void;
  onPageSizeChange: (pageSize: number) => void;
}) {
  const [draftPage, setDraftPage] = useState(String(page));

  useEffect(() => {
    setDraftPage(String(page));
  }, [page]);

  return (
    <div className="flex items-center justify-between gap-4 border-t border-white/10 px-5 py-4 text-sm text-slate-300">
      <div className="flex flex-wrap items-center gap-3">
        <span>
          페이지 {page} / {totalPages}
        </span>
        <span>총 {totalCount.toLocaleString()}명</span>
        <label className="flex items-center gap-2">
          <span>표시</span>
          <select
            className="rounded-full border border-white/10 bg-white/5 px-3 py-2 text-white outline-none"
            value={pageSize}
            onChange={(event) => onPageSizeChange(Number(event.target.value))}
          >
            {[25, 50, 100].map((size) => (
              <option
                key={size}
                value={size}
                className="bg-slate-900 text-white"
              >
                {size}
              </option>
            ))}
          </select>
        </label>
        <form
          className="flex items-center gap-2"
          onSubmit={(event) => {
            event.preventDefault();
            const nextPage = Number(draftPage);
            if (!Number.isFinite(nextPage)) return;
            onChange(Math.min(Math.max(nextPage, 1), totalPages));
          }}
        >
          <span>이동</span>
          <input
            className="w-20 rounded-full border border-white/10 bg-white/5 px-3 py-2 text-white outline-none"
            inputMode="numeric"
            value={draftPage}
            onChange={(event) => setDraftPage(event.target.value)}
          />
          <button
            type="submit"
            className="rounded-full border border-white/10 bg-white/5 px-3 py-2 text-white"
          >
            가기
          </button>
        </form>
      </div>
      <div className="flex gap-2">
        <button
          type="button"
          className="rounded-full border border-white/10 bg-white/5 px-3 py-2 disabled:opacity-40"
          disabled={page <= 1}
          onClick={() => onChange(page - 1)}
        >
          이전
        </button>
        <button
          type="button"
          className="rounded-full border border-white/10 bg-white/5 px-3 py-2 disabled:opacity-40"
          disabled={page >= totalPages}
          onClick={() => onChange(page + 1)}
        >
          다음
        </button>
      </div>
    </div>
  );
}
