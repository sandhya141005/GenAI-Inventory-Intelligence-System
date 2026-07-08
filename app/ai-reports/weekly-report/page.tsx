"use client";

import { useEffect, useState } from "react";
import { Sparkles, Loader2, Download } from "lucide-react";
import { CopilotResponse } from "@/lib/types";
import { fetchAI } from "@/lib/api";
import jsPDF from "jspdf";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

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

  function handleDownloadPDF() {
    if (!report) return;

    const doc = new jsPDF({ unit: "pt", format: "a4" });
    const pageWidth = doc.internal.pageSize.getWidth();
    const margin = 48;
    const maxWidth = pageWidth - margin * 2;
    let y = 60;

    doc.setFontSize(18);
    doc.setFont("helvetica", "bold");
    doc.text("Weekly Report", margin, y);
    y += 20;

    doc.setFontSize(10);
    doc.setFont("helvetica", "normal");
    doc.setTextColor(120);
    doc.text(`Generated: ${new Date().toLocaleString()}`, margin, y);
    y += 24;

    doc.setTextColor(0);
    doc.setFontSize(11);
    doc.setFont("helvetica", "bold");
    doc.text(`Intent: ${report.intent}`, margin, y);
    doc.text(`Confidence: ${report.confidence}`, pageWidth - margin - 140, y);
    y += 24;

    doc.setDrawColor(220);
    doc.line(margin, y, pageWidth - margin, y);
    y += 20;

    doc.setFontSize(11);
    doc.setFont("helvetica", "normal");
    const bodyLines: string[] = doc.splitTextToSize(report.response, maxWidth);

    bodyLines.forEach((line) => {
      if (y > doc.internal.pageSize.getHeight() - margin) {
        doc.addPage();
        y = 60;
      }
      doc.text(line, margin, y);
      y += 16;
    });

    if (Object.keys(report.metadata).length > 0) {
      y += 20;
      if (y > doc.internal.pageSize.getHeight() - margin) {
        doc.addPage();
        y = 60;
      }
      doc.setFont("helvetica", "bold");
      doc.text("Metadata", margin, y);
      y += 16;

      doc.setFont("courier", "normal");
      doc.setFontSize(9);
      const metaText = JSON.stringify(report.metadata, null, 2);
      const metaLines: string[] = doc.splitTextToSize(metaText, maxWidth);
      metaLines.forEach((line) => {
        if (y > doc.internal.pageSize.getHeight() - margin) {
          doc.addPage();
          y = 60;
        }
        doc.text(line, margin, y);
        y += 12;
      });
    }

    const dateStamp = new Date().toISOString().split("T")[0];
    doc.save(`weekly-report-${dateStamp}.pdf`);
  }

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
      <div className="flex items-center justify-between">
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
          <button
            onClick={handleDownloadPDF}
            className="flex items-center gap-2 rounded-md border border-border bg-surface px-3 py-2 text-sm font-medium text-ink hover:bg-gray-50 transition-colors"
          >
            <Download className="h-4 w-4" />
            Download PDF
          </button>
        )}
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

          <div className="prose prose-sm max-w-none text-ink leading-relaxed">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {report.response}
            </ReactMarkdown>
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