import { ArrowRight } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { fetchAnalytics } from "@/lib/api";

interface TransferItem {
  id: string;
  product: string;
  from: string;
  to: string;
  units: number;
  status: string;
  eta: string;
}

interface TransfersResponse {
  transfers: TransferItem[];
}

const statusVariant: Record<string, "success" | "warning" | "accent" | "neutral"> = {
  "In Transit": "accent",
  "Pending Approval": "warning",
  Completed: "success",
  Recommended: "warning",
};

export default async function TransfersPage() {
  const { transfers } = await fetchAnalytics<TransfersResponse>("/api/analytics/transfers");

  return (
    <div className="max-w-5xl mx-auto px-6 py-8 space-y-4">
      <div>
        <h1 className="text-lg font-semibold text-ink">Transfers</h1>
        <p className="text-sm text-ink-muted mt-1">
          Inventory movements from transfer records and rule-based imbalance detection.
        </p>
      </div>

      <div className="space-y-3">
        {transfers.map((t) => (
          <div key={t.id} className="rounded-lg border border-border bg-surface p-5 shadow-soft">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono text-ink-muted">{t.id}</span>
              <Badge variant={statusVariant[t.status] ?? "neutral"}>{t.status}</Badge>
            </div>
            <h3 className="mt-1 text-sm font-semibold text-ink">{t.product}</h3>
            <div className="mt-2 flex items-center gap-2 text-sm text-ink-muted">
              <span>{t.from}</span>
              <ArrowRight className="h-3.5 w-3.5" />
              <span>{t.to}</span>
              <span className="ml-2 font-medium text-ink">{t.units} units</span>
            </div>
            <div className="mt-3 flex items-center justify-between">
              <span className="text-xs text-ink-muted">ETA: {t.eta}</span>
              <Button size="sm" variant="secondary">
                View Details
              </Button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
