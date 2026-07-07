import { fetchAnalytics } from "@/lib/api";
import { TransferCard } from "@/components/transfer-card";

interface TransferItem {
  id: string;
  productId: number;
  product: string;
  fromStoreId: number;
  from: string;
  toStoreId: number;
  to: string;
  units: number;
  transferCost: number;
  revenueAtRisk: number;
  status: string;
  eta: string;
}

interface TransfersResponse {
  transfers: TransferItem[];
}

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
          <TransferCard key={t.id} transfer={t} />
        ))}
      </div>
    </div>
  );
}