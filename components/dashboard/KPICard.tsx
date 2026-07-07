import { KPI } from "@/lib/types";
import { ArrowDownRight, ArrowUpRight } from "lucide-react";
import { cn } from "@/lib/utils";

function Sparkline({ data, status }: { data: number[]; status: KPI["status"] }) {
  const width = 96;
  const height = 28;
  const min = Math.min(...data);
  const max = Math.max(...data);
  const range = max - min || 1;

  const points = data
    .map((value, i) => {
      const x = (i / (data.length - 1)) * width;
      const y = height - ((value - min) / range) * height;
      return `${x},${y}`;
    })
    .join(" ");

  const color =
    status === "risk" ? "#DC2626" : status === "watch" ? "#F59E0B" : "#22C55E";

  return (
    <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`}>
      <polyline
        points={points}
        fill="none"
        stroke={color}
        strokeWidth="1.75"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export function KPICard({ kpi }: { kpi: KPI }) {
  const isUp = kpi.trend >= 0;
  const trendIsGood =
    (kpi.id === "forecast-accuracy" || kpi.id === "inventory-health") ? isUp : !isUp;

  return (
    <div className="rounded-lg border border-border bg-surface p-4 shadow-soft">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-medium text-ink-muted">{kpi.label}</p>
          <p className="mt-1 text-2xl font-semibold text-ink">{kpi.value}</p>
        </div>
        <Sparkline data={kpi.trendData} status={kpi.status} />
      </div>

      <div className="mt-2 flex items-center gap-1 text-xs">
        {isUp ? (
          <ArrowUpRight
            className={cn("h-3.5 w-3.5", trendIsGood ? "text-success" : "text-danger")}
          />
        ) : (
          <ArrowDownRight
            className={cn("h-3.5 w-3.5", trendIsGood ? "text-success" : "text-danger")}
          />
        )}
        <span className={cn("font-medium", trendIsGood ? "text-success" : "text-danger")}>
          {Math.abs(kpi.trend)}%
        </span>
        <span className="text-ink-muted">vs last week</span>
      </div>

      <div className="mt-3 rounded-md bg-gray-50 p-2.5 text-xs leading-relaxed">
        <p className="font-medium text-ink-muted mb-0.5">Rule Explanation</p>
        <p className="text-ink">{kpi.explanation.why}</p>
        <p className="mt-1.5 font-medium text-ink-muted mb-0.5">Recommended Action</p>
        <p className="text-ink">{kpi.explanation.action}</p>
      </div>
    </div>
  );
}
