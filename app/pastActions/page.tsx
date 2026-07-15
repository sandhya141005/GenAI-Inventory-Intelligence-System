"use client";

import { useEffect, useState } from "react";
import { HandHeart, Truck, Mail, MapPin, X, Eye } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { fetchAI, fetchAnalytics } from "@/lib/api";
import { DonationHistoryItem } from "@/lib/types";

interface DonationHistoryResponse {
  items: DonationHistoryItem[];
}

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

type ViewKey = "donations" | "transfers" | null;

const statusVariant: Record<string, "success" | "warning" | "neutral" | "accent"> = {
  sent: "success",
  logged: "warning",
  completed: "success",
  pending: "warning",
  in_transit: "accent",
};

function formatTimestamp(value: string | null | undefined) {
  if (!value) return "Pending timestamp";
  return new Intl.DateTimeFormat("en-IN", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

export default function PastActionsPage() {
  const [activeView, setActiveView] = useState<ViewKey>(null);

  const [donations, setDonations] = useState<DonationHistoryItem[]>([]);
  const [donationsLoaded, setDonationsLoaded] = useState(false);
  const [donationsError, setDonationsError] = useState("");

  const [transfers, setTransfers] = useState<TransferItem[]>([]);
  const [transfersLoaded, setTransfersLoaded] = useState(false);
  const [transfersError, setTransfersError] = useState("");

  const [previewItem, setPreviewItem] = useState<{ type: "donation"; data: DonationHistoryItem } | { type: "transfer"; data: TransferItem } | null>(null);

  // Load counts for both boxes up front
  useEffect(() => {
    fetchAI<DonationHistoryResponse>("/api/donations/history")
      .then((data) => {
        setDonations(data.items ?? []);
        setDonationsLoaded(true);
      })
      .catch((err) => {
        setDonationsError(err instanceof Error ? err.message : "Unable to load donation history");
        setDonationsLoaded(true);
      });

    fetchAnalytics<TransfersResponse>("/api/analytics/transfers")
      .then((data) => {
        setTransfers(data.transfers ?? []);
        setTransfersLoaded(true);
      })
      .catch((err) => {
        setTransfersError(err instanceof Error ? err.message : "Unable to load transfers");
        setTransfersLoaded(true);
      });
  }, []);

  return (
    <div className="max-w-5xl mx-auto px-6 py-8 space-y-6">
      <div>
        <h1 className="text-lg font-semibold text-ink">Past Actions</h1>
        <p className="text-sm text-ink-muted mt-1">
          Review transfer movements and donation requests that have been sent or logged.
        </p>
      </div>

      {/* Two summary boxes */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <button
          onClick={() => setActiveView(activeView === "transfers" ? null : "transfers")}
          className={`text-left rounded-lg border p-5 shadow-soft transition ${
            activeView === "transfers"
              ? "border-primary bg-primary/5"
              : "border-border bg-surface hover:border-primary/50"
          }`}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Truck className="h-5 w-5 text-primary" />
              <h2 className="text-sm font-semibold text-ink">Transfer History</h2>
            </div>
            <Badge variant="accent">{transfersLoaded ? transfers.length : "…"}</Badge>
          </div>
          <p className="text-sm text-ink-muted mt-2">
            Inventory movements between stores based on transfer records.
          </p>
        </button>

        <button
          onClick={() => setActiveView(activeView === "donations" ? null : "donations")}
          className={`text-left rounded-lg border p-5 shadow-soft transition ${
            activeView === "donations"
              ? "border-primary bg-primary/5"
              : "border-border bg-surface hover:border-primary/50"
          }`}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <HandHeart className="h-5 w-5 text-primary" />
              <h2 className="text-sm font-semibold text-ink">Donation History</h2>
            </div>
            <Badge variant="accent">{donationsLoaded ? donations.length : "…"}</Badge>
          </div>
          <p className="text-sm text-ink-muted mt-2">
            Messages sent or logged for orphanage donation requests.
          </p>
        </button>
      </div>

      {/* Expanded list */}
      {activeView === "transfers" && (
        <div className="space-y-3">
          {transfersError && (
            <div className="rounded-md bg-danger/10 px-4 py-3 text-sm text-danger">{transfersError}</div>
          )}
          {transfersLoaded && transfers.length === 0 && !transfersError && (
            <div className="rounded-lg border border-border bg-surface p-6 text-sm text-ink-muted shadow-soft">
              No transfers recorded yet.
            </div>
          )}
          {transfers.map((t) => (
            <article
              key={t.id}
              className="rounded-lg border border-border bg-surface p-4 shadow-soft flex items-center justify-between gap-4"
            >
              <div className="space-y-1">
                <p className="text-sm font-semibold text-ink">{t.product}</p>
                <p className="text-xs text-ink-muted">
                  {t.from} → {t.to} · {t.units} units
                </p>
              </div>
              <div className="flex items-center gap-3">
                <Badge variant={statusVariant[t.status] ?? "neutral"}>{t.status}</Badge>
                <span className="text-xs text-ink-muted hidden sm:inline">{t.eta}</span>
                <button
                  onClick={() => setPreviewItem({ type: "transfer", data: t })}
                  className="inline-flex items-center gap-1 rounded-md border border-border px-3 py-1.5 text-xs font-medium text-ink hover:bg-gray-50"
                >
                  <Eye className="h-3.5 w-3.5" />
                  Preview
                </button>
              </div>
            </article>
          ))}
        </div>
      )}

      {activeView === "donations" && (
        <div className="space-y-3">
          {donationsError && (
            <div className="rounded-md bg-danger/10 px-4 py-3 text-sm text-danger">{donationsError}</div>
          )}
          {donationsLoaded && donations.length === 0 && !donationsError && (
            <div className="rounded-lg border border-border bg-surface p-6 text-sm text-ink-muted shadow-soft">
              No donation requests have been sent yet.
            </div>
          )}
          {donations.map((item) => (
            <article
              key={item.id}
              className="rounded-lg border border-border bg-surface p-4 shadow-soft flex flex-col gap-3 md:flex-row md:items-center md:justify-between"
            >
              <div className="space-y-1">
                <p className="text-sm font-semibold text-ink">{item.product_name}</p>
                <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-ink-muted">
                  <span className="inline-flex items-center gap-1">
                    <Mail className="h-3 w-3" />
                    {item.orphanage_name}
                  </span>
                  <span className="inline-flex items-center gap-1">
                    <MapPin className="h-3 w-3" />
                    {item.orphanage_city}
                  </span>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <Badge variant={statusVariant[item.status] ?? "neutral"}>{item.status}</Badge>
                <span className="text-xs text-ink-muted hidden sm:inline">
                  {formatTimestamp(item.created_at)}
                </span>
                <button
                  onClick={() => setPreviewItem({ type: "donation", data: item })}
                  className="inline-flex items-center gap-1 rounded-md border border-border px-3 py-1.5 text-xs font-medium text-ink hover:bg-gray-50"
                >
                  <Eye className="h-3.5 w-3.5" />
                  Preview
                </button>
              </div>
            </article>
          ))}
        </div>
      )}

      {/* Preview modal */}
      {previewItem && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4"
          onClick={() => setPreviewItem(null)}
        >
          <div
            className="w-full max-w-lg rounded-lg bg-surface p-6 shadow-lg"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-start justify-between">
              <h3 className="text-sm font-semibold text-ink">
                {previewItem.type === "donation" ? "Message Sent" : "Transfer Details"}
              </h3>
              <button onClick={() => setPreviewItem(null)} className="text-ink-muted hover:text-ink">
                <X className="h-4 w-4" />
              </button>
            </div>

            {previewItem.type === "donation" ? (
              <div className="mt-4 space-y-3">
                <div className="text-xs text-ink-muted">
                  To: {previewItem.data.orphanage_name} ({previewItem.data.orphanage_email})
                </div>
                <div className="rounded-md border border-border bg-gray-50 p-4">
                  <pre className="whitespace-pre-wrap break-words font-sans text-sm leading-relaxed text-ink">
                    {previewItem.data.message || "No message body was recorded."}
                  </pre>
                </div>
              </div>
            ) : (
              <div className="mt-4 space-y-2 text-sm text-ink">
                <p>
                  <span className="font-semibold">{previewItem.data.product}</span> —{" "}
                  {previewItem.data.units} units
                </p>
                <p className="text-ink-muted">
                  {previewItem.data.from} → {previewItem.data.to}
                </p>
                <p className="text-ink-muted">ETA: {previewItem.data.eta}</p>
                <p className="text-ink-muted">Transfer cost: ₹{previewItem.data.transferCost}</p>
                <p className="text-ink-muted">Revenue at risk: ₹{previewItem.data.revenueAtRisk}</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}