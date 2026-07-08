"use client";

import Link from "next/link";
import { FileText, BarChart3, ArrowRight } from "lucide-react";
import { cn } from "@/lib/utils";

const insightItems = [
  {
    href: "/reports",
    label: "Reports",
    description: "Generated summaries, exports, and scheduled reports for your inventory and sales.",
    icon: FileText,
    accent: "text-primary bg-primary/10",
  },
  {
    href: "/analytics",
    label: "Analytics",
    description: "Trends, breakdowns, and visual insights across stock, sales, and store performance.",
    icon: BarChart3,
    accent: "text-accent bg-accent/10",
  },
];

export default function InsightsPage() {
  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-lg font-semibold text-ink">Insights</h1>
        <p className="text-sm text-ink-muted mt-1">
          Reports and analytics for your inventory, in one place.
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 max-w-3xl">
        {insightItems.map((item) => {
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "group rounded-lg border border-border bg-surface p-5 shadow-soft",
                "hover:border-primary/30 hover:shadow-md transition-all"
              )}
            >
              <div className="flex items-start justify-between">
                <div className={cn("flex h-10 w-10 items-center justify-center rounded-md", item.accent)}>
                  <Icon className="h-5 w-5" strokeWidth={1.8} />
                </div>
                <ArrowRight
                  className="h-4 w-4 text-ink-muted opacity-0 -translate-x-1 group-hover:opacity-100 group-hover:translate-x-0 transition-all"
                  strokeWidth={1.8}
                />
              </div>

              <h3 className="mt-4 text-sm font-semibold text-ink">{item.label}</h3>
              <p className="mt-1.5 text-xs leading-relaxed text-ink-muted">
                {item.description}
              </p>
            </Link>
          );
        })}
      </div>
    </div>
  );
}