import { Recommendation } from "@/lib/types";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const priorityVariant: Record<Recommendation["priority"], "danger" | "warning" | "accent" | "neutral"> = {
  critical: "danger",
  high: "warning",
  medium: "accent",
  low: "neutral",
};

export function RecommendationCard({ rec }: { rec: Recommendation }) {
  return (
    <div className="rounded-lg border border-border bg-surface p-5 shadow-soft flex flex-col h-full">
      <div className="flex items-start justify-between gap-3">
        <h4 className="text-sm font-semibold text-ink">{rec.title}</h4>
        <Badge variant={priorityVariant[rec.priority]} className="capitalize shrink-0">
          {rec.priority}
        </Badge>
      </div>

      <p className="mt-2 text-sm text-ink-muted leading-relaxed">{rec.reason}</p>
      <p className="mt-2 text-sm text-ink leading-relaxed">{rec.impact}</p>

      <div className="mt-4 flex items-center gap-4 text-xs">
        <div>
          <span className="text-ink-muted">Confidence </span>
          <span className="font-semibold text-primary">{rec.confidence}%</span>
        </div>
        <div>
          <span className="text-ink-muted">Est. Savings </span>
          <span className="font-semibold text-success">{rec.estimatedSavings}</span>
        </div>
      </div>

      <div className="mt-4 flex gap-2 pt-4 border-t border-border mt-auto">
        <Button size="sm" variant="primary">
          {rec.primaryAction}
        </Button>
        <Button size="sm" variant="secondary">
          View Details
        </Button>
        <Button size="sm" variant="ghost">
          Dismiss
        </Button>
      </div>
    </div>
  );
}
