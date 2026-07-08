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
    status === "risk"
      ? "#DC2626"
      : status === "watch"
      ? "#F59E0B"
      : "#22C55E";

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

const explanationMap: Record<
  string,
  {
    why: string;
    action: string;
  }
> = {
  "revenue-at-risk": {
    why: "Estimated revenue that could be lost if high-demand products become unavailable due to insufficient inventory.",
    action:
      "Restock critical SKUs first and rebalance inventory between warehouses to reduce lost sales.",
  },

  "avg-days-of-coverage": {
    why: "Indicates how many days the current inventory can satisfy expected customer demand before replenishment is required.",
    action:
      "Monitor fast-moving items and schedule procurement before coverage drops below the desired threshold.",
  },

  "stockout-risk": {
    why: "Represents the percentage of inventory that is likely to experience stockouts based on current demand trends.",
    action:
      "Transfer stock from surplus locations or expedite purchase orders for high-risk products.",
  },

  "holding-cost": {
    why: "Measures the estimated storage and carrying costs associated with maintaining current inventory levels.",
    action:
      "Reduce excess inventory through transfers, promotions, or liquidation of slow-moving products.",
  },

  "inventory-health": {
    why: "A composite score reflecting inventory balance, product availability, and operational efficiency across all locations.",
    action:
      "Maintain balanced stock levels while minimizing both excess inventory and stockout risks.",
  },

  "inventory-turnover": {
    why: "Shows how efficiently inventory is sold and replenished over time. Higher turnover generally indicates better inventory utilization.",
    action:
      "Improve forecasting accuracy and reduce overstock to increase inventory movement.",
  },

  "store-health-score": {
    why: "Evaluates overall store performance by considering stock availability, sales consistency, and inventory utilization.",
    action:
      "Focus on stores with lower performance by optimizing replenishment and inventory allocation.",
  },
};

export function KPICard({ kpi }: { kpi: KPI }) {
  const isUp = kpi.trend >= 0;

  const trendIsGood =
    kpi.id === "forecast-accuracy" ||
    kpi.id === "inventory-health" ||
    kpi.id === "store-health-score"
      ? isUp
      : !isUp;

  const explanation =
    explanationMap[kpi.id.toLowerCase()] ?? kpi.explanation;

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
            className={cn(
              "h-3.5 w-3.5",
              trendIsGood ? "text-success" : "text-danger"
            )}
          />
        ) : (
          <ArrowDownRight
            className={cn(
              "h-3.5 w-3.5",
              trendIsGood ? "text-success" : "text-danger"
            )}
          />
        )}

        <span
          className={cn(
            "font-medium",
            trendIsGood ? "text-success" : "text-danger"
          )}
        >
          {Math.abs(kpi.trend)}%
        </span>

        <span className="text-ink-muted">vs last week</span>
      </div>

      <div className="mt-3 rounded-md bg-gray-50 p-2.5 text-xs leading-relaxed">
        <p className="mb-0.5 font-medium text-ink-muted">
          Rule Explanation
        </p>

        <p className="text-ink">{explanation.why}</p>

        <p className="mt-2 font-medium text-ink-muted">
          Recommended Action
        </p>

        <p className="text-ink">{explanation.action}</p>
      </div>
    </div>
  );
}