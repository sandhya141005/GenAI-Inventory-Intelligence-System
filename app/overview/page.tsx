"use client";

import { useEffect, useState } from "react";
import { Sparkles } from "lucide-react";
import { KPICard } from "@/components/dashboard/KPICard";
import { RecommendationCard } from "@/components/dashboard/RecommendationCard";
import { SuggestedActionsSection } from "@/components/dashboard/SuggestedActionsSection";
import { fetchAnalytics } from "@/lib/api";
import { InventoryActionSuggestion, KPI, Recommendation } from "@/lib/types";

interface OverviewResponse {
  summary: {
    generatedAt: string;
    headline: string;
    detail: string;
  };
  kpis: KPI[];
  recommendations: Recommendation[];
  actionSuggestions: InventoryActionSuggestion[];
}

export default function OverviewPage() {
  const [overview, setOverview] = useState<OverviewResponse | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchAnalytics<OverviewResponse>("/api/analytics/overview")
      .then(setOverview)
      .catch((err) => setError(err instanceof Error ? err.message : "Unable to load overview"));
  }, []);

  const summary = overview?.summary ?? {
    generatedAt: "",
    headline: "Loading inventory overview...",
    detail: "StockLens is preparing your scoped dashboard.",
  };
  const kpis = overview?.kpis ?? [];
  const recommendations = overview?.recommendations ?? [];
  const actionSuggestions = overview?.actionSuggestions ?? [];

  return (
    <div className="max-w-5xl mx-auto px-6 py-8 space-y-10">
      <section className="rounded-lg border border-border bg-surface p-6 shadow-soft">
        <div className="flex items-center gap-2 text-xs font-medium text-primary">
          <Sparkles className="h-3.5 w-3.5" />
          Executive Summary - Generated {summary.generatedAt}
        </div>
        <h1 className="mt-2 text-xl font-semibold text-ink leading-snug">
          {summary.headline}
        </h1>
        <p className="mt-2 text-sm text-ink-muted leading-relaxed">
          {summary.detail}
        </p>
      </section>
      {error && <div className="rounded-md bg-danger/10 px-4 py-3 text-sm text-danger">{error}</div>}

      <SuggestedActionsSection suggestions={actionSuggestions} />

      <section>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-sm font-semibold text-ink">Today's Overview</h2>
          <span className="text-xs text-ink-muted">Live from PostgreSQL</span>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
          {kpis.map((kpi) => (
            <KPICard key={kpi.id} kpi={kpi} />
          ))}
        </div>
      </section>

      <section>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-sm font-semibold text-ink">Today's Recommendations</h2>
          <span className="text-xs text-ink-muted">
            {recommendations.length} actions available
          </span>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {recommendations.map((rec) => (
            <RecommendationCard key={rec.id} rec={rec} />
          ))}
        </div>
      </section>
    </div>
  );
}
