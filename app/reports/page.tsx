
"use client";

import { useEffect, useState } from "react";
import { fetchAnalytics } from "@/lib/api";
import { ReportSummary } from "@/lib/types";
import { ReportCard } from "@/components/report-card";
interface ReportsResponse {
  reports: ReportSummary[];
}

export default function ReportsPage() {
  const [reports, setReports] = useState<ReportSummary[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchAnalytics<ReportsResponse>("/api/analytics/reports")
      .then((data) => setReports(data.reports ?? []))
      .catch((err) => setError(err instanceof Error ? err.message : "Unable to load reports"));
  }, []);

  return (
    <div className="max-w-4xl mx-auto px-6 py-8 space-y-4">
      <div>
        <h1 className="text-lg font-semibold text-ink">Reports</h1>
        <p className="text-sm text-ink-muted mt-1">
          Generated automatically from live inventory data.
        </p>
      </div>
      {error && <div className="rounded-md bg-danger/10 px-4 py-3 text-sm text-danger">{error}</div>}

      <div className="space-y-3">
       <div className="space-y-3">
  {reports.map((report) => (
    <ReportCard
      key={report.id}
      report={report}
    />
  ))}
</div>
      </div>
    </div>
  );
}
