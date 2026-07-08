"use client";

import { useEffect, useState } from "react";
import { RecommendationCard } from "@/components/dashboard/RecommendationCard";
// import { KPICard } from "@/components/dashboard/KPICard";
import { fetchAnalytics } from "@/lib/api";
import { Recommendation, KPI, InventoryActionSuggestion } from "@/lib/types";
import { SuggestedActionsSection } from "@/components/dashboard/SuggestedActionsSection";

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

export default function RecommendationsPage() {
  const [overview, setOverview] = useState<OverviewResponse | null>(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchAnalytics<OverviewResponse>("/api/analytics/overview")
      .then((data) => setOverview(data))
      .catch((err) =>
        setError(err instanceof Error ? err.message : "Unable to load recommendations")
      )
      .finally(() => setIsLoading(false));
  }, []);

  // const kpis = overview?.kpis ?? [];
  const recommendations = overview?.recommendations ?? [];
  // const recommendations = overview?.recommendations ?? [];
  const actionSuggestions = overview?.actionSuggestions ?? [];

  return (
    <div className="max-w-5xl mx-auto px-6 py-8 space-y-4">
      <div>
        <h1 className="text-lg font-semibold text-ink">Recommendations</h1>
        <p className="text-sm text-ink-muted mt-1">
          Actionable, ranked by priority and confidence.
        </p>
      </div>

      {error && (
        <div className="rounded-md bg-danger/10 px-4 py-3 text-sm text-danger">{error}</div>
      )}

      {isLoading && !error && (
        <div className="text-sm text-ink-muted">Loading overview…</div>
      )}

      {!isLoading && !error && (
        <>
          <SuggestedActionsSection suggestions={actionSuggestions} />
          {/* <section>
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
          </section> */}
        </>
      )}
    </div>
  );
}