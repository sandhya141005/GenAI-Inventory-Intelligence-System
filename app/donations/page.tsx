import { HandHeart, Mail, MapPin } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { fetchAI } from "@/lib/api";
import { DonationHistoryItem } from "@/lib/types";

interface DonationHistoryResponse {
  items: DonationHistoryItem[];
}

const statusVariant: Record<string, "success" | "warning" | "neutral" | "accent"> = {
  sent: "success",
  logged: "warning",
};

function formatTimestamp(value: string | null) {
  if (!value) return "Pending timestamp";
  return new Intl.DateTimeFormat("en-IN", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

export default async function DonationsPage() {
  const { items } = await fetchAI<DonationHistoryResponse>("/api/donations/history");

  return (
    <div className="max-w-5xl mx-auto px-6 py-8 space-y-5">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-lg font-semibold text-ink">Donation History</h1>
          <p className="text-sm text-ink-muted mt-1">
            Messages sent or logged for orphanage donation requests.
          </p>
        </div>
        <Badge variant="accent">{items.length} requests</Badge>
      </div>

      {items.length === 0 ? (
        <div className="rounded-lg border border-border bg-surface p-6 text-sm text-ink-muted shadow-soft">
          No donation requests have been sent yet.
        </div>
      ) : (
        <div className="space-y-3">
          {items.map((item) => (
            <article key={item.id} className="rounded-lg border border-border bg-surface p-5 shadow-soft">
              <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <HandHeart className="h-4 w-4 text-primary" />
                    <h2 className="text-sm font-semibold text-ink">{item.product_name}</h2>
                  </div>
                  <div className="flex flex-wrap gap-x-4 gap-y-1 text-sm text-ink-muted">
                    <span className="inline-flex items-center gap-1">
                      <Mail className="h-3.5 w-3.5" />
                      {item.orphanage_name} ({item.orphanage_email})
                    </span>
                    <span className="inline-flex items-center gap-1">
                      <MapPin className="h-3.5 w-3.5" />
                      {item.orphanage_city}
                    </span>
                  </div>
                </div>
                <div className="flex items-center gap-2 md:justify-end">
                  <Badge variant={statusVariant[item.status] ?? "neutral"}>{item.status}</Badge>
                  <span className="text-xs text-ink-muted">{formatTimestamp(item.created_at)}</span>
                </div>
              </div>

              <div className="mt-4 rounded-md border border-border bg-gray-50 p-4">
                <p className="text-xs font-semibold uppercase tracking-wide text-ink-muted">Message Sent</p>
                <pre className="mt-2 whitespace-pre-wrap break-words font-sans text-sm leading-relaxed text-ink">
                  {item.message || "No message body was recorded."}
                </pre>
              </div>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
