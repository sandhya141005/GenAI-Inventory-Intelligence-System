"use client";

import { useState } from "react";
import { ArrowRight, X, Loader2, CheckCircle2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

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

const statusVariant: Record<string, "success" | "warning" | "accent" | "neutral"> = {
  "In Transit": "accent",
  "Pending Approval": "warning",
  Completed: "success",
  Recommended: "warning",
};

export function TransferCard({ transfer }: { transfer: TransferItem }) {
  const [status, setStatus] = useState(transfer.status);
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const isRecommended = status === "Recommended";
  const isDone = status === "Completed";

  const handleInitiate = async () => {
    setLoading(true);
    setError(null);
    try {
      const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
      const headers: HeadersInit = { "Content-Type": "application/json" };
      if (token) {
        headers["Authorization"] = `Bearer ${token}`;
      }
      const res = await fetch("/api/transfers/initiate", {
        method: "POST",
        headers,
        body: JSON.stringify({
          productId: transfer.productId,
          fromStoreId: transfer.fromStoreId,
          toStoreId: transfer.toStoreId,
          units: transfer.units,
          transferCost: transfer.transferCost,
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data?.detail ?? "Transfer failed");
      setStatus("Completed");
      setOpen(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Transfer failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <div
        className={`rounded-lg border p-5 shadow-soft transition-colors ${
          isDone ? "border-success/40 bg-success/5" : "border-border bg-surface"
        }`}
      >
        <div className="flex items-center justify-between">
          <span className="text-xs font-mono text-ink-muted">{transfer.id}</span>
          <Badge variant={statusVariant[status] ?? "neutral"}>
            {isDone && <CheckCircle2 className="h-3 w-3 mr-1 inline" />}
            {status}
          </Badge>
        </div>
        <h3 className="mt-1 text-sm font-semibold text-ink">{transfer.product}</h3>
        <div className="mt-2 flex items-center gap-2 text-sm text-ink-muted">
          <span>{transfer.from}</span>
          <ArrowRight className="h-3.5 w-3.5" />
          <span>{transfer.to}</span>
          <span className="ml-2 font-medium text-ink">{transfer.units} units</span>
        </div>
        <div className="mt-3 flex items-center justify-between">
          <span className="text-xs text-ink-muted">ETA: {transfer.eta}</span>
          <Button size="sm" variant="secondary" onClick={() => setOpen(true)}>
            View Details
          </Button>
        </div>
      </div>

      {open && (
        <div
          className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-6"
          onClick={() => setOpen(false)}
        >
          <div
            className="bg-surface w-full max-w-lg rounded-lg shadow-xl overflow-hidden"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between px-6 py-4 border-b border-border">
              <h2 className="text-base font-semibold text-ink">{transfer.id}</h2>
              <button onClick={() => setOpen(false)} className="text-ink-muted hover:text-ink">
                <X className="h-4 w-4" />
              </button>
            </div>

            <div className="px-6 py-5 space-y-4 text-sm">
              <div>
                <p className="text-xs text-ink-muted">Product</p>
                <p className="font-medium text-ink">{transfer.product}</p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="rounded-md border border-border p-3">
                  <p className="text-xs text-ink-muted">Sender</p>
                  <p className="font-medium text-ink">{transfer.from}</p>
                </div>
                <div className="rounded-md border border-border p-3">
                  <p className="text-xs text-ink-muted">Receiver</p>
                  <p className="font-medium text-ink">{transfer.to}</p>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div>
                  <p className="text-xs text-ink-muted">Stock to Send</p>
                  <p className="font-medium text-ink">{transfer.units} units</p>
                </div>
                <div>
                  <p className="text-xs text-ink-muted">Transfer Cost</p>
                  <p className="font-medium text-ink">INR {transfer.transferCost.toLocaleString()}</p>
                </div>
                <div>
                  <p className="text-xs text-ink-muted">Revenue at Risk</p>
                  <p className="font-medium text-red-500">
                    INR {transfer.revenueAtRisk.toLocaleString()}
                  </p>
                </div>
              </div>

              <div>
                <p className="text-xs text-ink-muted">ETA</p>
                <p className="font-medium text-ink">{transfer.eta}</p>
              </div>

              {error && <p className="text-xs text-red-500">{error}</p>}
            </div>

            <div className="px-6 py-4 border-t border-border flex justify-end gap-2">
              <Button size="sm" variant="ghost" onClick={() => setOpen(false)}>
                Close
              </Button>
              {isRecommended && (
                <Button size="sm" onClick={handleInitiate} disabled={loading}>
                  {loading && <Loader2 className="h-3.5 w-3.5 mr-1 animate-spin" />}
                  Initiate Transfer
                </Button>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
}