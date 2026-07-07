import { RecommendationCard } from "@/components/dashboard/RecommendationCard";
import { fetchAnalytics } from "@/lib/api";
import { Recommendation } from "@/lib/types";

interface RecommendationsResponse {
  recommendations: Recommendation[];
}

export default async function RecommendationsPage() {
  const { recommendations } = await fetchAnalytics<RecommendationsResponse>("/api/analytics/recommendations");

  return (
    <div className="max-w-5xl mx-auto px-6 py-8 space-y-4">
      <div>
        <h1 className="text-lg font-semibold text-ink">Recommendations</h1>
        <p className="text-sm text-ink-muted mt-1">
          Actionable, ranked by priority and confidence.
        </p>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {recommendations.map((rec) => (
          <RecommendationCard key={rec.id} rec={rec} />
        ))}
      </div>
    </div>
  );
}
