export type Confidence = number; // 0-100

export type Priority = "critical" | "high" | "medium" | "low";

export interface KPI {
  id: string;
  label: string;
  value: string;
  trend: number; // percentage, signed
  trendData: number[]; // sparkline points
  status: "good" | "watch" | "risk";
  explanation: {
    why: string;
    action: string;
  };
}

export interface Recommendation {
  id: string;
  title: string;
  reason: string;
  impact: string;
  priority: Priority;
  confidence: Confidence;
  estimatedSavings: string;
  primaryAction: string;
}

export interface InventoryItem {
  sku: string;
  product: string;
  store: string;
  inventory: number;
  demand: number;
  daysOfCover: number;
  health: "healthy" | "low" | "critical" | "overstock";
  revenueAtRisk: number;
  status: "in-stock" | "at-risk" | "stockout" | "overstock";
}

export interface ChatAction {
  label: string;
  variant: "primary" | "secondary";
}

export interface ChatInsight {
  title: string;
  metricLabel: string;
  metricValue: string;
  reason: string;
  recommendation: string;
  confidence: Confidence;
  estimatedSavings: string;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  text: string;
  insight?: ChatInsight;
  actions?: ChatAction[];
  timestamp: string;
}

export interface ReportSummary {
  id: string;
  title: string;
  summary: string;
  generatedBy: string;
  lastUpdated: string;
}

export interface NoticeItem {
  id: string;
  category: "Critical Alert" | "Recommendation" | "Transfer" | "Stockout" | "Completed";
  title: string;
  detail: string;
  timestamp: string;
}

export interface CopilotResponse {
  intent: string;
  response: string;
  conversation_id?: number;
  metadata: Record<string, any>;
  confidence: "low" | "medium" | "high";
}

export interface User {
  id: number;
  email: string;
  full_name: string;
  is_active: boolean;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
}
