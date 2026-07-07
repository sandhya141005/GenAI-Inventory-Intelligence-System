"use client";

import { useEffect, useState } from "react";
import { RecommendationCard } from "@/components/dashboard/RecommendationCard";
import { fetchAnalytics } from "@/lib/api";
import { Recommendation } from "@/lib/types";

interface RecommendationsResponse {
  recommendations: Recommendation[];
}

export default function RecommendationsPage() {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchAnalytics<RecommendationsResponse>("/api/analytics/recommendations")
      .then((data) => setRecommendations(data.recommendations ?? []))
      .catch((err) => setError(err instanceof Error ? err.message : "Unable to load recommendations"));
  }, []);

  return (
    <div className="max-w-5xl mx-auto px-6 py-8 space-y-4">
      <div>
        <h1 className="text-lg font-semibold text-ink">Recommendations</h1>
        <p className="text-sm text-ink-muted mt-1">
          Actionable, ranked by priority and confidence.
        </p>
      </div>
      {error && <div className="rounded-md bg-danger/10 px-4 py-3 text-sm text-danger">{error}</div>}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {recommendations.map((rec) => (
          <RecommendationCard key={rec.id} rec={rec} />
        ))}
      </div>
    </div>
  );
}
