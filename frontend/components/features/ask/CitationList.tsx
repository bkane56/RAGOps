import type { AskResponse } from "@/lib/types/api";

export function CitationList({ citations }: { citations: AskResponse["citations"] }) {
  if (!citations.length) return null;
  return (
    <ul className="mt-2 flex flex-wrap gap-2 text-sm" data-testid="citation-list">
      {citations.map((c) => (
        <li
          key={c.chunk_id}
          className="rounded bg-panel px-2 py-1 text-accent"
        >
          {c.label} chunk {c.chunk_id.slice(0, 8)}
        </li>
      ))}
    </ul>
  );
}
