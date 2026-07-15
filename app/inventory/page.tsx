"use client";

import { useEffect, useState } from "react";
import { InventoryTable } from "@/components/inventory/InventoryTable";
import { fetchAnalytics } from "@/lib/api";
import { InventoryItem } from "@/lib/types";

interface InventoryResponse {
  items: InventoryItem[];
}

export default function InventoryPage() {
  const [items, setItems] = useState<InventoryItem[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchAnalytics<InventoryResponse>("/api/analytics/inventory")
      .then((data) => setItems(data.items ?? []))
      .catch((err) => setError(err instanceof Error ? err.message : "Unable to load inventory"));
  }, []);

  return (
    <div className="max-w-6xl mx-auto px-6 py-8 space-y-4">
      <div>
        <h1 className="text-lg font-semibold text-ink">Inventory</h1>
        <p className="text-sm text-ink-muted mt-1">
          Live inventory position across all stores. Select a row to ask the
          decision engine for a deeper explanation.
        </p>
      </div>
      {error && <div className="rounded-md bg-danger/10 px-4 py-3 text-sm text-danger">{error}</div>}
      <InventoryTable data={items} />
    </div>
  );
}
