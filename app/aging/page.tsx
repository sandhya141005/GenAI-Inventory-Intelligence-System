"use client";

import { useEffect, useState } from "react";
import { Badge } from "@/components/ui/badge";
import { fetchAnalytics } from "@/lib/api";
import { formatCurrency } from "@/lib/utils";

interface AgingItem {
  product: string;
  store: string;
  ageDays: number;
  value: number;
  band: string;
}

interface AgingResponse {
  items: AgingItem[];
}

const bandVariant: Record<string, "danger" | "warning" | "accent" | "neutral"> = {
  "90+ days": "danger",
  "60-90 days": "warning",
  "30-60 days": "accent",
  "0-30 days": "neutral",
};

export default function AgingPage() {
  const [items, setItems] = useState<AgingItem[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchAnalytics<AgingResponse>("/api/analytics/inventory-aging")
      .then((data) => setItems(data.items ?? []))
      .catch((err) => setError(err instanceof Error ? err.message : "Unable to load inventory aging"));
  }, []);

  return (
    <div className="max-w-5xl mx-auto px-6 py-8 space-y-4">
      <div>
        <h1 className="text-lg font-semibold text-ink">Inventory Aging</h1>
        <p className="text-sm text-ink-muted mt-1">
          Stock tying up working capital, ranked by age.
        </p>
      </div>
      {error && <div className="rounded-md bg-danger/10 px-4 py-3 text-sm text-danger">{error}</div>}

      <div className="rounded-lg border border-border bg-surface shadow-soft divide-y divide-border">
        {items.map((item) => (
          <div key={`${item.product}-${item.store}`} className="flex items-center justify-between p-4">
            <div>
              <p className="text-sm font-medium text-ink">{item.product}</p>
              <p className="text-xs text-ink-muted mt-0.5">{item.store}</p>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-xs text-ink-muted">{item.ageDays} days</span>
              <span className="text-sm font-semibold text-ink">{formatCurrency(item.value)}</span>
              <Badge variant={bandVariant[item.band] ?? "neutral"}>{item.band}</Badge>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
