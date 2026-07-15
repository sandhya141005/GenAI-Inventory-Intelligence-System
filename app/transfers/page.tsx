"use client";

import { useEffect, useState } from "react";
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

export default function TransfersPage() {
  const [transfers, setTransfers] = useState<TransferItem[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchAnalytics<TransfersResponse>("/api/analytics/transfers")
      .then((data) => setTransfers(data.transfers ?? []))
      .catch((err) => setError(err instanceof Error ? err.message : "Unable to load transfers"));
  }, []);

  return (
    <div className="max-w-5xl mx-auto px-6 py-8 space-y-4">
      <div>
        <h1 className="text-lg font-semibold text-ink">Transfers</h1>
        <p className="text-sm text-ink-muted mt-1">
          Inventory movements from transfer records and rule-based imbalance detection.
        </p>
      </div>
      {error && <div className="rounded-md bg-danger/10 px-4 py-3 text-sm text-danger">{error}</div>}

      <div className="space-y-3">
        {transfers.map((t) => (
          <TransferCard key={t.id} transfer={t} />
        ))}
      </div>
    </div>
  );
}
