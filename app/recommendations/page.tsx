"use client";

import { useEffect, useState } from "react";
import { fetchAnalytics } from "@/lib/api";
import { InventoryActionSuggestion } from "@/lib/types";
import { SuggestedActionsSection } from "@/components/dashboard/SuggestedActionsSection";

interface ActionsResponse {
  suggestions: InventoryActionSuggestion[];
}

export default function RecommendationsPage() {
  const [suggestions, setSuggestions] = useState<InventoryActionSuggestion[]>([]);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchAnalytics<ActionsResponse>("/api/analytics/actions")
      .then((data) => setSuggestions(data.suggestions ?? []))
      .catch((err) =>
        setError(err instanceof Error ? err.message : "Unable to load recommendations")
      )
      .finally(() => setIsLoading(false));
  }, []);

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
        <div className="text-sm text-ink-muted">Loading recommendations...</div>
      )}

      {!isLoading && !error && (
        <SuggestedActionsSection suggestions={suggestions} />
      )}
    </div>
  );
}
