"use client";

import { useEffect, useState } from "react";
import { Sparkles, Loader2, Download } from "lucide-react";
import { CopilotResponse } from "@/lib/types";
import { fetchAI } from "@/lib/api";
import jsPDF from "jspdf";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export default function ExecutiveSummaryPage() {
  const [report, setReport] = useState<CopilotResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [isDownloading, setIsDownloading] = useState(false);

  useEffect(() => {
    async function loadReport() {
      try {
        const data = await fetchAI<CopilotResponse>("/api/copilot/executive-summary");
        setReport(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load executive summary");
      } finally {
        setIsLoading(false);
      }
    }
    loadReport();
  }, []);

  function handleDownloadPDF() {
    if (!report) return;
    setIsDownloading(true);

    try {
      const doc = new jsPDF({
        unit: "pt",
        format: "a4",
      });

      const pageWidth = doc.internal.pageSize.getWidth();
      const pageHeight = doc.internal.pageSize.getHeight();
      const margin = 48;
      const contentWidth = pageWidth - margin * 2;
      let cursorY = margin;

      // Helper to add a new page when content overflows
      function ensureSpace(neededHeight: number) {
        if (cursorY + neededHeight > pageHeight - margin) {
          doc.addPage();
          cursorY = margin;
        }
      }

      // Title
      doc.setFont("helvetica", "bold");
      doc.setFontSize(18);
      doc.setTextColor(20, 20, 20);
      doc.text("Executive Summary", margin, cursorY);
      cursorY += 22;

      doc.setFont("helvetica", "normal");
      doc.setFontSize(10);
      doc.setTextColor(120, 120, 120);
      doc.text("AI-generated strategic inventory overview", margin, cursorY);
      cursorY += 24;

      // Divider
      doc.setDrawColor(220, 220, 220);
      doc.line(margin, cursorY, pageWidth - margin, cursorY);
      cursorY += 20;

      // Intent + Confidence row
      doc.setFont("helvetica", "bold");
      doc.setFontSize(10);
      doc.setTextColor(90, 90, 90);
      doc.text(`INTENT: ${report.intent.toUpperCase()}`, margin, cursorY);

      const confidenceText = `CONFIDENCE: ${report.confidence.toUpperCase()}`;
      const confidenceWidth = doc.getTextWidth(confidenceText);
      const confidenceColor: [number, number, number] =
        report.confidence === "high"
          ? [22, 163, 74]
          : report.confidence === "medium"
          ? [217, 119, 6]
          : [220, 38, 38];
      doc.setTextColor(...confidenceColor);
      doc.text(confidenceText, pageWidth - margin - confidenceWidth, cursorY);
      cursorY += 20;

      doc.setDrawColor(230, 230, 230);
      doc.line(margin, cursorY, pageWidth - margin, cursorY);
      cursorY += 24;

      // Body / response text
      doc.setFont("helvetica", "normal");
      doc.setFontSize(11);
      doc.setTextColor(30, 30, 30);

      const bodyLines = doc.splitTextToSize(report.response, contentWidth);
      const lineHeight = 16;

      bodyLines.forEach((line: string) => {
        ensureSpace(lineHeight);
        doc.text(line, margin, cursorY);
        cursorY += lineHeight;
      });

      // Metadata section
      const metadataEntries = Object.entries(report.metadata || {});
      if (metadataEntries.length > 0) {
        cursorY += 16;
        ensureSpace(30);

        doc.setDrawColor(220, 220, 220);
        doc.line(margin, cursorY, pageWidth - margin, cursorY);
        cursorY += 20;

        doc.setFont("helvetica", "bold");
        doc.setFontSize(10);
        doc.setTextColor(90, 90, 90);
        doc.text("METADATA", margin, cursorY);
        cursorY += 18;

        doc.setFont("courier", "normal");
        doc.setFontSize(9);
        doc.setTextColor(70, 70, 70);

        const metadataText = JSON.stringify(report.metadata, null, 2);
        const metadataLines = doc.splitTextToSize(metadataText, contentWidth);

        metadataLines.forEach((line: string) => {
          ensureSpace(13);
          doc.text(line, margin, cursorY);
          cursorY += 13;
        });
      }

      // Footer with generation date on every page
      const pageCount = doc.getNumberOfPages();
      for (let i = 1; i <= pageCount; i++) {
        doc.setPage(i);
        doc.setFont("helvetica", "normal");
        doc.setFontSize(8);
        doc.setTextColor(160, 160, 160);
        doc.text(
          `Generated on ${new Date().toLocaleString()}`,
          margin,
          pageHeight - 24
        );
        doc.text(`Page ${i} of ${pageCount}`, pageWidth - margin - 60, pageHeight - 24);
      }

      const filename = `executive-summary-${new Date()
        .toISOString()
        .slice(0, 10)}.pdf`;
      doc.save(filename);
    } finally {
      setIsDownloading(false);
    }
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
            <h1 className="text-lg font-semibold text-ink">Executive Summary</h1>
            <p className="text-sm text-ink-muted">AI-generated strategic inventory overview</p>
          </div>
        </div>

        {report && (
          <button
            onClick={handleDownloadPDF}
            disabled={isDownloading}
            className="flex items-center gap-2 rounded-lg border border-border bg-surface px-4 py-2 text-sm font-medium text-ink shadow-soft hover:bg-gray-50 disabled:opacity-60 disabled:cursor-not-allowed"
          >
            {isDownloading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Download className="h-4 w-4" />
            )}
            {isDownloading ? "Preparing..." : "Download PDF"}
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