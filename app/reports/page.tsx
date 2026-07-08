
// "use client";

// import { useEffect, useState } from "react";
// import { fetchAnalytics } from "@/lib/api";
// import { ReportSummary } from "@/lib/types";
// import { ReportCard } from "@/components/report-card";
// interface ReportsResponse {
//   reports: ReportSummary[];
// }

// export default function ReportsPage() {
//   const [reports, setReports] = useState<ReportSummary[]>([]);
//   const [error, setError] = useState("");

//   useEffect(() => {
//     fetchAnalytics<ReportsResponse>("/api/analytics/reports")
//       .then((data) => setReports(data.reports ?? []))
//       .catch((err) => setError(err instanceof Error ? err.message : "Unable to load reports"));
//   }, []);

//   return (
//     <div className="max-w-4xl mx-auto px-6 py-8 space-y-4">
//       <div>
//         <h1 className="text-lg font-semibold text-ink">Reports</h1>
//         <p className="text-sm text-ink-muted mt-1">
//           Generated automatically from live inventory data.
//         </p>
//       </div>
//       {error && <div className="rounded-md bg-danger/10 px-4 py-3 text-sm text-danger">{error}</div>}

//       <div className="space-y-3">
//        <div className="space-y-3">
//   {reports.map((report) => (
//     <ReportCard
//       key={report.id}
//       report={report}
//     />
//   ))}
// </div>
//       </div>
//     </div>
//   );
// }


"use client";

import Link from "next/link";
import { Sparkles, FileText, CalendarDays } from "lucide-react";

const reportLinks = [
  {
    title: "Morning Brief",
    description: "A quick daily snapshot of key metrics and updates.",
    href: "/ai-reports/morning-brief",
    icon: Sparkles,
  },
  {
    title: "Executive Summary",
    description: "High-level overview for leadership and stakeholders.",
    href: "/ai-reports/executive-summary",
    icon: FileText,
  },
  {
    title: "Weekly Report",
    description: "Detailed breakdown of performance over the past week.",
    href: "/ai-reports/weekly-report",
    icon: CalendarDays,
  },
];

export default function ReportsPage() {
  return (
    <div className="max-w-4xl mx-auto px-6 py-8 space-y-6">
      <div>
        <h1 className="text-lg font-semibold text-ink">AI Reports</h1>
        <p className="text-sm text-ink-muted mt-1">
          Choose a report to view.
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {reportLinks.map(({ title, description, href, icon: Icon }) => (
          <Link
            key={href}
            href={href}
            className="group rounded-lg border border-border bg-surface p-5 flex flex-col gap-3 hover:border-primary hover:shadow-sm transition-all"
          >
            <div className="w-10 h-10 rounded-md bg-primary/10 flex items-center justify-center text-primary group-hover:bg-primary group-hover:text-white transition-colors">
              <Icon className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-sm font-semibold text-ink">{title}</h2>
              <p className="text-xs text-ink-muted mt-1">{description}</p>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}