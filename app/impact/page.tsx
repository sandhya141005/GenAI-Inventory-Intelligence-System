// app/impact/page.tsx
"use client";
console.log("Impact page rendered");
import type { ValueType, NameType } from "recharts/types/component/DefaultTooltipContent";

import { useEffect, useState } from "react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  RadialBarChart, RadialBar, PolarAngleAxis, Cell,
} from "recharts";
import { fetchAnalytics } from "@/lib/api";

interface ImpactData {
  revenue: { protected_value: number; risk_reduction_percent: number };
  cost: {
    inventory_value_released: number;
    inventory_release_percent: number;
    holding_cost_saved: number;
    holding_cost_reduction_percent: number;
  };
  risk: { stockout_risk_reduction_percent: number; overstock_reduction_percent: number };
  sustainability: { waste_prevented_units: number; recovery_rate_percent: number };
  dataset: {
    total_inventory_value: number;
    total_revenue_at_risk: number;
    total_holding_cost: number;
    distressed_inventory_value: number;
  };
  notes: { evaluation_horizon_days: number; donation_value_basis: string };
}

const currency = (v: number) => `₹${v.toLocaleString("en-IN", { maximumFractionDigits: 0 })}`;

function Card({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="rounded-lg border border-border bg-white p-5 shadow-sm">
      <h3 className="mb-4 text-sm font-semibold text-ink">{title}</h3>
      {children}
    </div>
  );
}

/* ---------- Revenue: Dumbbell (before vs after risk) ---------- */
function DumbbellChart({ before, after }: { before: number; after: number }) {
  const max = Math.max(before, after, 1);
  const pct = (v: number) => `${(v / max) * 100}%`;
  return (
    <div className="space-y-4">
      <div className="relative h-10">
        <div className="absolute inset-y-0 left-0 right-0 flex items-center">
          <div className="h-1 w-full rounded bg-slate-100" />
        </div>
        <div
          className="absolute top-1/2 h-1 -translate-y-1/2 rounded bg-blue-200"
          style={{ left: pct(after), width: `calc(${pct(before)} - ${pct(after)})` }}
        />
        <div
          className="absolute top-1/2 h-3 w-3 -translate-y-1/2 -translate-x-1/2 rounded-full bg-slate-400"
          style={{ left: pct(before) }}
          title="Before"
        />
        <div
          className="absolute top-1/2 h-3 w-3 -translate-y-1/2 -translate-x-1/2 rounded-full bg-blue-600"
          style={{ left: pct(after) }}
          title="After"
        />
      </div>
      <div className="flex justify-between text-xs text-ink-muted">
        <span><span className="inline-block h-2 w-2 rounded-full bg-slate-400 mr-1" />Before: {currency(before)}</span>
        <span><span className="inline-block h-2 w-2 rounded-full bg-blue-600 mr-1" />After: {currency(after)}</span>
      </div>
      <p className="text-2xl font-semibold text-blue-600">{currency(before - after)} <span className="text-sm font-normal text-ink-muted">protected</span></p>
    </div>
  );
}

/* ---------- Cost: Bullet chart ---------- */
function BulletChart({ label, value, target }: { label: string; value: number; target: number }) {
  const max = Math.max(value, target, 1) * 1.15;
  return (
    <div className="mb-4 last:mb-0">
      <div className="mb-1 flex justify-between text-xs text-ink-muted">
        <span>{label}</span>
        <span className="font-medium text-ink">{currency(value)}</span>
      </div>
      <div className="relative h-4 rounded bg-slate-100">
        <div className="absolute inset-y-0 left-0 rounded bg-blue-500" style={{ width: `${(value / max) * 100}%` }} />
        <div className="absolute inset-y-0 w-0.5 bg-slate-700" style={{ left: `${(target / max) * 100}%` }} />
      </div>
    </div>
  );
}

/* ---------- Risk: Gauges ---------- */
function Gauge({ label, percent }: { label: string; percent: number }) {
  const data = [{ name: label, value: percent, fill: percent >= 50 ? "#2563eb" : "#f59e0b" }];
  return (
    <div className="flex flex-col items-center">
      <ResponsiveContainer width="100%" height={120}>
        <RadialBarChart innerRadius="70%" outerRadius="100%" data={data} startAngle={180} endAngle={0}>
          <PolarAngleAxis type="number" domain={[0, 100]} angleAxisId={0} tick={false} />
          <RadialBar background dataKey="value" cornerRadius={8} />
        </RadialBarChart>
      </ResponsiveContainer>
      <p className="-mt-8 text-xl font-semibold text-ink">{percent.toFixed(1)}%</p>
      <p className="mt-1 text-xs text-ink-muted">{label}</p>
    </div>
  );
}

/* ---------- Sustainability: Progress ---------- */
function Progress({ label, percent, sublabel }: { label: string; percent: number; sublabel?: string }) {
  return (
    <div className="mb-4 last:mb-0">
      <div className="mb-1 flex justify-between text-xs text-ink-muted">
        <span>{label}</span>
        <span className="font-medium text-ink">{percent.toFixed(1)}%</span>
      </div>
      <div className="h-2.5 rounded-full bg-slate-100">
        <div className="h-2.5 rounded-full bg-green-500 transition-all" style={{ width: `${Math.min(percent, 100)}%` }} />
      </div>
      {sublabel && <p className="mt-1 text-xs text-ink-muted">{sublabel}</p>}
    </div>
  );
}

/* ---------- Waterfall ---------- */
function WaterfallChart({ before, transfer, clearance, donation, after }: {
  before: number; transfer: number; clearance: number; donation: number; after: number;
}) {
  let running = before;
  const steps = [
    { name: "Before", start: 0, value: before, fill: "#94a3b8" },
    { name: "Transfer", start: (running -= transfer), value: transfer, fill: "#3b82f6" },
    { name: "Clearance", start: (running -= clearance), value: clearance, fill: "#22c55e" },
    { name: "Donation", start: (running -= donation), value: donation, fill: "#f59e0b" },
    { name: "After", start: 0, value: after, fill: "#2563eb" },
  ];
  return (
    <ResponsiveContainer width="100%" height={260}>
      <BarChart data={steps} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" vertical={false} />
        <XAxis dataKey="name" tick={{ fontSize: 12 }} />
        <YAxis tick={{ fontSize: 12 }} tickFormatter={(v) => `₹${(v / 1000).toFixed(0)}k`} />
       <Tooltip
  formatter={(value, name) => [
    `₹${Number(value).toLocaleString("en-IN")}`,
    String(name),
  ]}
/>
        <Bar dataKey="start" stackId="a" fill="transparent" />
        <Bar dataKey="value" stackId="a" radius={[4, 4, 0, 0]}>
          {steps.map((s, i) => <Cell key={i} fill={s.fill} />)}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}

export default function ImpactPage() {
    console.log("Impact component rendered");
  const [data, setData] = useState<ImpactData | null>(null);
  const [industryPool, setIndustryPool] = useState(740_000_000_000); // illustrative, editable

  useEffect(() => {
    console.log("useEffect running");
    fetchAnalytics<ImpactData>("/api/public/impact").then(setData).catch(console.error);
  }, []);

  if (!data) {
    return <div className="p-6 text-sm text-ink-muted">Loading decision impact evaluation…</div>;
  }

const before = data.revenue.before_revenue_at_risk;
const after = data.revenue.after_revenue_at_risk;
  const recoveryRate = data.sustainability.recovery_rate_percent;
  const projectedOpportunity = industryPool * (recoveryRate / 100);

  return (
    <div className="mx-auto max-w-6xl space-y-6 p-6">
      <div>
        <h1 className="text-xl font-semibold text-ink">Decision Impact Evaluation</h1>
        <p className="text-sm text-ink-muted">
          Measured business improvement from applying every current recommendation — {data.notes.evaluation_horizon_days}-day horizon.
        </p>
      </div>

      {/* Row 1: Revenue + Cost */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card title="Revenue">
          <DumbbellChart before={before} after={after} />
        </Card>
        <Card title="Cost">
          <BulletChart label="Inventory Value Released" value={data.cost.inventory_value_released} target={data.dataset.total_inventory_value} />
          <BulletChart label="Holding Cost Saved (30d)" value={data.cost.holding_cost_saved} target={data.dataset.total_holding_cost} />
        </Card>
      </div>

      {/* Row 2: Risk + Sustainability */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card title="Risk">
          <div className="grid grid-cols-2 gap-4">
            <Gauge label="Stockout Risk Reduction" percent={data.risk.stockout_risk_reduction_percent} />
            <Gauge label="Overstock Reduction" percent={data.risk.overstock_reduction_percent} />
          </div>
        </Card>
        <Card title="Sustainability">
          <Progress
            label="Recovery Rate"
            percent={data.sustainability.recovery_rate_percent}
            sublabel="(Transfer + Clearance + Donation value) / Distressed inventory value"
          />
          <Progress
            label="Waste Prevented"
            percent={Math.min(100, (data.sustainability.waste_prevented_units / 1000) * 100)}
            sublabel={`${data.sustainability.waste_prevented_units.toLocaleString()} units diverted from write-off`}
          />
        </Card>
      </div>

      {/* Waterfall */}
      <Card title="Revenue at Risk — Waterfall">
        <WaterfallChart
          before={before}
          transfer={data.revenue.transfer_revenue_protected}
          clearance={data.cost.inventory_value_released * 0.01}
          donation={0}
          after={after}
        />
        <p className="mt-2 text-xs text-ink-muted">
          Transfer bar reflects revenue directly protected via inter-store moves. Clearance/donation reduce distressed inventory value, tracked separately in Cost and Sustainability.
        </p>
      </Card>

      {/* Measured -> Industry projection */}
      <Card title="Measured Improvement → Industry Scale Projection">
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
          <div>
            <p className="text-xs uppercase tracking-wide text-ink-muted">Measured in this dataset</p>
            <p className="mt-1 text-3xl font-semibold text-blue-600">{recoveryRate.toFixed(1)}%</p>
            <p className="text-sm text-ink-muted">recovery rate on {currency(data.dataset.distressed_inventory_value)} distressed inventory</p>
          </div>
          <div>
            <p className="text-xs uppercase tracking-wide text-ink-muted">Illustrative industry extrapolation</p>
            <p className="mt-1 text-3xl font-semibold text-ink">{currency(projectedOpportunity / 1e9)}B</p>
            <p className="text-sm text-ink-muted">
              if applied to a ${(industryPool / 1e9).toFixed(0)}B excess-inventory pool — <span className="italic">for illustration only, not a forecast</span>
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
}
