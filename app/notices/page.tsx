import { AlertTriangle, ArrowLeftRight, CheckCircle2, Lightbulb, PackageX } from "lucide-react";
import { Button } from "@/components/ui/button";
import { fetchAnalytics } from "@/lib/api";
import { NoticeItem } from "@/lib/types";

const iconFor: Record<NoticeItem["category"], typeof AlertTriangle> = {
  "Critical Alert": AlertTriangle,
  Recommendation: Lightbulb,
  Transfer: ArrowLeftRight,
  Stockout: PackageX,
  Completed: CheckCircle2,
};

const colorFor: Record<NoticeItem["category"], string> = {
  "Critical Alert": "text-danger bg-danger/10",
  Recommendation: "text-accent bg-accent/10",
  Transfer: "text-primary bg-primary/10",
  Stockout: "text-warning bg-warning/10",
  Completed: "text-success bg-success/10",
};

interface NoticesResponse {
  notices: NoticeItem[];
}

export default async function NoticesPage() {
  const { notices } = await fetchAnalytics<NoticesResponse>("/api/analytics/notices");

  return (
    <div className="max-w-4xl mx-auto px-6 py-8 space-y-4">
      <div>
        <h1 className="text-lg font-semibold text-ink">Notice Board</h1>
        <p className="text-sm text-ink-muted mt-1">
          Alerts, recommendations, and updates across the network.
        </p>
      </div>

      <div className="space-y-2">
        {notices.map((notice) => {
          const Icon = iconFor[notice.category];
          return (
            <div
              key={notice.id}
              className="flex items-start gap-3 rounded-lg border border-border bg-surface p-4 shadow-soft"
            >
              <div className={`h-8 w-8 rounded-md flex items-center justify-center shrink-0 ${colorFor[notice.category]}`}>
                <Icon className="h-4 w-4" />
              </div>
              <div className="flex-1">
                <div className="flex items-center justify-between">
                  <p className="text-sm font-medium text-ink">{notice.title}</p>
                  <span className="text-xs text-ink-muted shrink-0 ml-2">
                    {notice.timestamp}
                  </span>
                </div>
                <p className="text-sm text-ink-muted mt-0.5">{notice.detail}</p>
                <Button size="sm" variant="subtle" className="mt-2">
                  Inspect
                </Button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
