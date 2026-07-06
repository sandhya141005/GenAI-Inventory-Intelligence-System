"use client";

import { useEffect, useState } from "react";
import { Sparkles, Loader2 } from "lucide-react";
import { CopilotResponse } from "@/lib/types";
import { fetchAI } from "@/lib/api";

export default function WeeklyReportPage() {
  const [report, setReport] = useState<CopilotResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadReport() {
      try {
        const data = await fetchAI<CopilotResponse>("/api/copilot/weekly-report");
        setReport(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load weekly report");
      } finally {
        setIsLoading(false);
      }
    }
    loadReport();
  }, []);

  if (isLoading) {
    return (
      <div className="flex h-[calc(100vh-64px)] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-4xl mx-auto px-6 py-8">
        <div className="rounded-lg bg-danger/10 px-4 py-3 text-sm text-danger">
          {error}
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-6 py-8 space-y-6">
      <div className="flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary">
          <Sparkles className="h-5 w-5 text-white" />
        </div>
        <div>
          <h1 className="text-lg font-semibold text-ink">Weekly Report</h1>
          <p className="text-sm text-ink-muted">AI-generated weekly inventory and revenue performance</p>
        </div>
      </div>

      {report && (
        <div className="rounded-lg border border-border bg-surface p-6 shadow-soft space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-ink-muted uppercase tracking-wide">
              Intent: {report.intent}
            </span>
            <span className={`text-xs font-semibold uppercase ${
              report.confidence === "high" ? "text-success" :
              report.confidence === "medium" ? "text-accent" : "text-warning"
            }`}>
              Confidence: {report.confidence}
            </span>
          </div>

          <div className="prose prose-sm max-w-none text-ink leading-relaxed whitespace-pre-wrap">
            {report.response}
          </div>

          {Object.keys(report.metadata).length > 0 && (
            <div className="pt-4 border-t border-border">
              <p className="text-xs font-medium text-ink-muted mb-2">Metadata</p>
              <pre className="text-xs text-ink-muted bg-gray-50 p-3 rounded overflow-x-auto">
                {JSON.stringify(report.metadata, null, 2)}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
