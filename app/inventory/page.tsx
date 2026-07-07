import { InventoryTable } from "@/components/inventory/InventoryTable";
import { fetchAnalytics } from "@/lib/api";
import { InventoryItem } from "@/lib/types";

interface InventoryResponse {
  items: InventoryItem[];
}

export default async function InventoryPage() {
  const { items } = await fetchAnalytics<InventoryResponse>("/api/analytics/inventory");

  return (
    <div className="max-w-6xl mx-auto px-6 py-8 space-y-4">
      <div>
        <h1 className="text-lg font-semibold text-ink">Inventory</h1>
        <p className="text-sm text-ink-muted mt-1">
          Live inventory position across all stores. Select a row to ask the
          decision engine for a deeper explanation.
        </p>
      </div>
      <InventoryTable data={items} />
    </div>
  );
}
