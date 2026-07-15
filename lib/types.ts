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

export type InventoryActionType = "CLEARANCE_SALE" | "DONATE" | "DISCARD";

export interface InventoryActionSuggestion {
  product_id: number;
  store_id?: number | null;
  product_name: string;
  category: string;
  action: InventoryActionType;
  reason: string;
  discount_percent: number | null;
  suggested_recipient: string | null;
  current_stock_qty: number;
  store_city: string | null;
  pickup_location: string;
}

export interface DonationHistoryItem {
  id: number;
  product_id: number;
  product_name: string;
  orphanage_name: string;
  orphanage_city: string;
  orphanage_email: string;
  status: "sent" | "logged" | string;
  message: string | null;
  created_at: string | null;
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

// lib/types.ts
export interface ReportSummary {
  id: string;
  title: string;
  summary: string;
  content: string; // full report body — markdown or plain text
  lastUpdated: string;
  generatedBy: string;
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

export interface ChatHistoryMessage {
  id: number;
  role: "user" | "assistant";
  content: string;
  created_at: string;
  metadata?: Record<string, any> | null;
}

export interface ChatHistoryConversation {
  conversation_id: number;
  title?: string | null;
  created_at: string;
  updated_at: string;
  messages: ChatHistoryMessage[];
}

export interface ChatHistoryResponse {
  conversations: ChatHistoryConversation[];
}

export interface User {
  id: number;
  email: string;
  full_name: string;
  is_active: boolean;
  realm_id: number | null;
  role: "WAREHOUSE_OWNER" | "STORE_MANAGER" | null;
  assigned_store_id: number | null;
  assigned_store_name: string | null;
  realm_name: string | null;
  industry_tag: string | null;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
}
