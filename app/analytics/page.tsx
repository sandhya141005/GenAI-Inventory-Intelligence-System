"use client";

import { useEffect, useState } from "react";
import ReactECharts from "echarts-for-react";
import { fetchAnalytics } from "@/lib/api";

interface ChartsResponse {
  revenueTrend: { labels: string[]; values: number[] };
  storePerformance: { labels: string[]; values: number[] };
  categoryMix: { labels: string[]; values: number[] };
}

function ChartCard({ title, option, height = 260 }: { title: string; option: object; height?: number }) {
  return (
    <div className="rounded-lg border border-border bg-surface p-5 shadow-soft">
      <h3 className="text-sm font-semibold text-ink mb-2">{title}</h3>
      <ReactECharts option={option} style={{ height }} />
    </div>
  );
}

export default function AnalyticsPage() {
  const [charts, setCharts] = useState<ChartsResponse | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchAnalytics<ChartsResponse>("/api/analytics/charts")
      .then((data) => {
        setCharts(data);
        setError("");
      })
      .catch((err) => setError(err instanceof Error ? err.message : "Unable to load analytics charts"));
  }, []);

  const revenueTrend = {
    tooltip: { trigger: "axis" },
    grid: { left: 40, right: 20, top: 20, bottom: 30 },
    xAxis: { type: "category", data: charts?.revenueTrend.labels ?? [] },
    yAxis: { type: "value", splitLine: { lineStyle: { color: "#F1F5F9" } } },
    series: [{ name: "Revenue", type: "line", smooth: true, data: charts?.revenueTrend.values ?? [], lineStyle: { color: "#0057B8", width: 2 } }],
  };

  const storePerformance = {
    tooltip: { trigger: "axis" },
    grid: { left: 80, right: 20, top: 20, bottom: 30 },
    xAxis: { type: "value", splitLine: { lineStyle: { color: "#F1F5F9" } } },
    yAxis: { type: "category", data: charts?.storePerformance.labels ?? [] },
    series: [{ type: "bar", data: charts?.storePerformance.values ?? [], itemStyle: { color: "#0078D4", borderRadius: [0, 4, 4, 0] }, barWidth: 16 }],
  };

  const categoryMix = {
    tooltip: { trigger: "item" },
    legend: { bottom: 0, textStyle: { color: "#6B7280", fontSize: 11 } },
    series: [{ type: "pie", radius: ["45%", "70%"], label: { show: false }, data: (charts?.categoryMix.labels ?? []).map((name, index) => ({ name, value: charts?.categoryMix.values[index] ?? 0 })) }],
  };

  return (
    <div className="max-w-6xl mx-auto px-6 py-8 space-y-4">
      <div>
        <h1 className="text-lg font-semibold text-ink">Analytics</h1>
        <p className="text-sm text-ink-muted mt-1">
          Supporting detail behind the deterministic recommendations.
        </p>
      </div>

      {error && <div className="rounded-md bg-danger/10 px-4 py-3 text-sm text-danger">{error}</div>}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <ChartCard title="Revenue Trend (7 days)" option={revenueTrend} />
        <ChartCard title="Store Performance Index" option={storePerformance} />
      </div>
      <ChartCard title="Inventory Category Mix" option={categoryMix} height={300} />
    </div>
  );
}
