/**
 * StatusBadge.jsx — Green / Yellow / Red status pill.
 */

export default function StatusBadge({ status, size = "sm" }) {
  const base = size === "lg" ? "px-3 py-1 text-sm font-semibold" : "px-2 py-0.5 text-xs font-semibold";
  const colors = {
    green: "bg-green-100 text-green-800",
    yellow: "bg-yellow-100 text-yellow-800",
    red: "bg-red-100 text-red-700",
  };
  const labels = { green: "Good", yellow: "Due Soon", red: "Overdue" };

  return (
    <span className={`inline-block rounded-full ${base} ${colors[status] || colors.green}`}>
      {labels[status] || status}
    </span>
  );
}
