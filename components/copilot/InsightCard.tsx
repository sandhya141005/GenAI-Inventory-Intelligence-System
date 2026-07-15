import { ChatInsight } from "@/lib/types";
import { Button } from "@/components/ui/button";

export function InsightCard({ insight }: { insight: ChatInsight }) {
  return (
    <div className="mt-3 rounded-md border border-border bg-gray-50/60 p-4 animate-fade-in">
      <p className="text-xs font-medium text-ink-muted uppercase tracking-wide">
        {insight.title}
      </p>
      <p className="mt-1 text-2xl font-semibold text-ink">
        {insight.metricValue}
      </p>

      <div className="mt-3 space-y-2 text-sm">
        <div>
          <span className="text-ink-muted">Reason </span>
          <span className="text-ink">{insight.reason}</span>
        </div>
        <div>
          <span className="text-ink-muted">Recommendation </span>
          <span className="text-ink">{insight.recommendation}</span>
        </div>
      </div>

      <div className="mt-3 flex items-center gap-4 text-xs">
        <div className="flex items-center gap-1.5">
          <span className="text-ink-muted">Confidence</span>
          <span className="font-semibold text-primary">
            {insight.confidence}%
          </span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="text-ink-muted">Est. Savings</span>
          <span className="font-semibold text-success">
            {insight.estimatedSavings}
          </span>
        </div>
      </div>

      <div className="mt-3 flex gap-2">
        <Button size="sm" variant="primary">
          Transfer Inventory
        </Button>
        <Button size="sm" variant="secondary">
          View Details
        </Button>
      </div>
    </div>
  );
}
