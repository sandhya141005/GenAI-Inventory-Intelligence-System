"use client";

import {  useEffect, useMemo, useState } from "react";
import { AlertTriangle, Gift, Megaphone, Send, Trash2, ChevronDown } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { fetchAI } from "@/lib/api";
import { InventoryActionSuggestion, InventoryActionType } from "@/lib/types";
import { ArrowRightLeft } from "lucide-react";
import { fetchAnalytics } from "@/lib/api";
import { TransferCard } from "@/components/transfer-card";

interface SuggestedActionsSectionProps {
  suggestions: InventoryActionSuggestion[];
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
// Add this near your other type definitions
type ActionOrTransfer = InventoryActionType | "TRANSFER";
const ACTION_META = {
  CLEARANCE_SALE: {
    label: "Clearance Sale",
    boxLabel: "Sale Suggestions",
    badge: "accent",
    icon: Megaphone,
  },
  DONATE: {
    label: "Donate",
    boxLabel: "Donation Suggestions",
    badge: "success",
    icon: Gift,
  },
  DISCARD: {
    label: "Discard",
    boxLabel: "Discard Suggestions",
    badge: "danger",
    icon: Trash2,
  },
  TRANSFER: {
    label: "Transfer",
    boxLabel: "Transfer Suggestions",
    badge: "neutral",
    icon: ArrowRightLeft,
  },
} as const;



const ACTION_ORDER: ActionOrTransfer[] = [
  "CLEARANCE_SALE",
  "DONATE",
  "DISCARD",
  "TRANSFER",
];
const BOX_STYLES: Record<ActionOrTransfer, string> = {
  CLEARANCE_SALE: "border-accent/30 bg-accent/5",
  DONATE: "border-success/30 bg-success/5",
  DISCARD: "border-danger/30 bg-danger/5",
  TRANSFER: "border-primary/30 bg-primary/5",
};

const BOX_ICON_STYLES: Record<ActionOrTransfer, string> = {
  CLEARANCE_SALE: "bg-accent/10 text-accent",
  DONATE: "bg-success/10 text-success",
  DISCARD: "bg-danger/10 text-danger",
  TRANSFER: "bg-primary/10 text-primary",
};

export function SuggestedActionsSection({ suggestions }: SuggestedActionsSectionProps) {
  const [pendingProductId, setPendingProductId] = useState<number | null>(null);
  const [messages, setMessages] = useState<Record<number, string>>({});
  const [expandedAction, setExpandedAction] = useState<ActionOrTransfer | null>(null);
  const [transfers, setTransfers] = useState<TransferItem[]>([]);

  const grouped = useMemo(() => {
  return ACTION_ORDER.map((action) => ({
    action,
    items:
      action === "TRANSFER"
        ? transfers
        : suggestions.filter((suggestion) => suggestion.action === action),
  }));
}, [suggestions, transfers]);

  useEffect(() => {
  fetchAnalytics<TransfersResponse>("/api/analytics/transfers")
    .then((data) => setTransfers(data.transfers ?? []))
    .catch(() => {});
}, []);


  async function notifyOrphanages(productId: number) {
    setPendingProductId(productId);
    setMessages((current) => ({ ...current, [productId]: "" }));

    try {
      const result = await fetchAI<{ detail: string }>("/api/donations/notify", {
        method: "POST",
        body: JSON.stringify({ product_id: productId }),
      });
      setMessages((current) => ({ ...current, [productId]: result.detail }));
    } catch (error) {
      const detail = error instanceof Error ? error.message : "Notification failed";
      setMessages((current) => ({ ...current, [productId]: detail }));
    } finally {
      setPendingProductId(null);
    }
  }

  function toggleAction(action: ActionOrTransfer) {
  setExpandedAction((current) => (current === action ? null : action));
}

  if (suggestions.length === 0) {
    return (
      <section>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-sm font-semibold text-ink">Suggested Actions</h2>
          <span className="text-xs text-ink-muted">0 actions available</span>
        </div>
        <div className="rounded-lg border border-border bg-surface p-5 text-sm text-ink-muted shadow-soft">
          No clearance, donation, or discard actions are needed right now.
        </div>
      </section>
    );
  }

  return (
  <section>
    <div className="flex items-center justify-between mb-3">
      <h2 className="text-sm font-semibold text-ink">Suggested Actions</h2>
      <span className="text-xs text-ink-muted">{suggestions.length} actions available</span>
    </div>

    <div className="space-y-3">
      {grouped.map(({ action, items }) => {
        if (items.length === 0) return null;

        const meta = ACTION_META[action];
        const Icon = meta.icon;
        const isExpanded = expandedAction === action;

        return (
          <div
            key={action}
            className={`rounded-lg border ${BOX_STYLES[action]} p-4 shadow-soft`}
          >
            <button
              type="button"
              onClick={() => toggleAction(action)}
              className="flex w-full items-center justify-between"
            >
              <div className="flex items-center gap-2">
                <span
                  className={`flex h-8 w-8 items-center justify-center rounded-full ${BOX_ICON_STYLES[action]}`}
                >
                  <Icon className="h-4 w-4" />
                </span>
                <span className="text-sm font-semibold text-ink">{meta.boxLabel}</span>
                <Badge variant="neutral">{items.length}</Badge>
              </div>
              <ChevronDown
                className={`h-4 w-4 text-ink-muted transition-transform ${
                  isExpanded ? "rotate-180" : ""
                }`}
              />
            </button>

            {isExpanded ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                {action === "TRANSFER"
                  ? (items as TransferItem[]).map((transfer) => (
                      <TransferCard key={transfer.id} transfer={transfer} />
                    ))
                  : (items as InventoryActionSuggestion[]).map((suggestion) => (
                      <article
                        key={`${suggestion.action}-${suggestion.product_id}`}
                        className="rounded-lg border border-border bg-surface p-4 shadow-soft"
                      >
                        <div className="flex items-start justify-between gap-3">
                          <div>
                            <h4 className="text-sm font-semibold text-ink">
                              {suggestion.product_name}
                            </h4>
                            <p className="mt-1 text-xs text-ink-muted">
                              {suggestion.category} / {suggestion.pickup_location}
                            </p>
                          </div>
                          <Badge variant={meta.badge}>{meta.label}</Badge>
                        </div>

                        <p className="mt-3 text-sm leading-relaxed text-ink-muted">
                          {suggestion.reason}
                        </p>

                        {suggestion.suggested_recipient ? (
                          <p className="mt-2 text-xs font-medium text-ink">
                            Suggested recipient: {suggestion.suggested_recipient}
                          </p>
                        ) : null}

                        <div className="mt-4 flex flex-wrap items-center gap-2">
                          {suggestion.discount_percent ? (
                            <Badge variant="warning">
                              {suggestion.discount_percent}% off
                            </Badge>
                          ) : null}

                          <Badge variant="neutral">
                            {suggestion.current_stock_qty} units
                          </Badge>

                          {suggestion.action === "DISCARD" ? (
                            <Badge variant="danger">
                              <AlertTriangle className="mr-1 h-3 w-3" />
                              Expired
                            </Badge>
                          ) : null}
                        </div>

                        {suggestion.action === "DONATE" ? (
                          <div className="mt-4 space-y-2">
                            <Button
                              type="button"
                              size="sm"
                              variant="secondary"
                              onClick={() => notifyOrphanages(suggestion.product_id)}
                              disabled={pendingProductId === suggestion.product_id}
                            >
                              <Send className="h-3.5 w-3.5" />
                              {pendingProductId === suggestion.product_id
                                ? "Notifying..."
                                : "Notify Nearby Orphanages"}
                            </Button>

                            {messages[suggestion.product_id] ? (
                              <p className="text-xs text-green-700">
                                {messages[suggestion.product_id]}
                              </p>
                            ) : null}
                          </div>
                        ) : null}
                      </article>
                    ))}
              </div>
            ) : null}
          </div>
        );
      })}
    </div>
  </section>
);
}