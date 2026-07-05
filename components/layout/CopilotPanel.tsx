"use client";

import { useEffect, useRef, useState } from "react";
import { Send, Sparkles } from "lucide-react";
import { ChatMessage, KPI, Recommendation } from "@/lib/types";
import { ChatMessageBubble, TypingIndicator } from "@/components/copilot/ChatMessage";
import { SuggestedPrompts } from "@/components/copilot/SuggestedPrompts";
import { Button } from "@/components/ui/button";

const suggestedPrompts = [
  "What products are likely to stock out?",
  "Show products with highest revenue at risk.",
  "Recommend inventory transfers.",
  "Generate today's executive summary.",
  "Which stores require replenishment?",
  "Identify slow-moving inventory.",
];

interface OverviewResponse {
  summary: {
    headline: string;
    detail: string;
  };
  kpis: KPI[];
  recommendations: Recommendation[];
}

function timestamp() {
  return new Date().toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" });
}

async function buildAssistantResponse(prompt: string): Promise<ChatMessage> {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
  const response = await fetch(`${apiUrl}/api/analytics/overview`, { cache: "no-store" });

  if (!response.ok) {
    throw new Error("Unable to load decision intelligence metrics");
  }

  const data = (await response.json()) as OverviewResponse;
  const revenueAtRisk = data.kpis.find((kpi) => kpi.id === "revenue-at-risk");
  const firstRecommendation = data.recommendations[0];

  return {
    id: crypto.randomUUID(),
    role: "assistant",
    text: `Decision engine result for "${prompt}": ${data.summary.headline}`,
    timestamp: timestamp(),
    insight: firstRecommendation
      ? {
          title: firstRecommendation.title,
          metricLabel: revenueAtRisk?.label ?? "Revenue at Risk",
          metricValue: revenueAtRisk?.value ?? "INR 0",
          reason: firstRecommendation.reason,
          recommendation: firstRecommendation.primaryAction,
          confidence: firstRecommendation.confidence,
          estimatedSavings: firstRecommendation.estimatedSavings,
        }
      : undefined,
  };
}

export function CopilotPanel() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "initial-live-decision-engine",
      role: "assistant",
      text: "Ask a question to query the live decision engine. Responses are calculated from PostgreSQL analytics endpoints.",
      timestamp: timestamp(),
    },
  ]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);

  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, isTyping]);

  async function handleSend(text: string) {
    const trimmed = text.trim();

    if (!trimmed) return;

    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      text: trimmed,
      timestamp: timestamp(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsTyping(true);

    try {
      const assistantMessage = await buildAssistantResponse(trimmed);
      setMessages((prev) => [...prev, assistantMessage]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          text: "The decision engine is not reachable right now. Start the FastAPI service and try again.",
          timestamp: timestamp(),
        },
      ]);
    } finally {
      setIsTyping(false);
    }
  }

  return (
    <div className="flex h-full flex-col bg-background">
      <div className="border-b border-border bg-white px-8 py-6">
        <div className="flex items-center gap-4">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary">
            <Sparkles className="h-6 w-6 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-foreground">Inventory Decision Engine</h1>
            <p className="mt-1 text-sm text-muted-foreground">
              Query live inventory, stockout, transfer, replenishment, and revenue-risk metrics.
            </p>
          </div>
        </div>
      </div>

      <div ref={scrollRef} className="flex-1 overflow-y-auto px-8 py-8">
        <div className="mx-auto max-w-5xl space-y-6">
          {messages.map((message) => (
            <ChatMessageBubble key={message.id} message={message} />
          ))}
          {isTyping && <TypingIndicator />}
          {messages.length === 1 && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold">Suggested Questions</h3>
              <SuggestedPrompts prompts={suggestedPrompts} onSelect={handleSend} />
            </div>
          )}
        </div>
      </div>

      <div className="border-t border-border bg-white px-8 py-5">
        <div className="mx-auto max-w-5xl">
          <form
            onSubmit={(event) => {
              event.preventDefault();
              handleSend(input);
            }}
            className="flex items-center gap-3"
          >
            <input
              value={input}
              onChange={(event) => setInput(event.target.value)}
              placeholder="Ask the decision engine..."
              className="h-14 flex-1 rounded-xl border border-border bg-background px-5 text-sm outline-none transition focus:ring-2 focus:ring-primary/30"
            />
            <Button type="submit" size="lg" className="h-14 w-14 rounded-xl">
              <Send className="h-5 w-5" />
            </Button>
          </form>
        </div>
      </div>
    </div>
  );
}
