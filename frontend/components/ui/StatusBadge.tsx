interface StatusBadgeProps {
  status: string;
}

const styles: Record<string, string> = {
  ready: "bg-emerald-900/50 text-emerald-300",
  processing: "bg-amber-900/50 text-amber-300",
  pending: "bg-slate-700 text-slate-300",
  failed: "bg-red-900/50 text-red-300",
};

export function StatusBadge({ status }: StatusBadgeProps) {
  const cls = styles[status] || "bg-slate-700 text-slate-300";
  return (
    <span className={`inline-block rounded px-2 py-0.5 text-xs font-medium ${cls}`}>
      {status}
    </span>
  );
}
