"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { History, Plus, Send, Sparkles } from "lucide-react";
import { ChatHistoryConversation, ChatMessage, CopilotResponse } from "@/lib/types";
import { ChatMessageBubble, TypingIndicator } from "@/components/copilot/ChatMessage";
import { SuggestedPrompts } from "@/components/copilot/SuggestedPrompts";
import { Button } from "@/components/ui/button";
import { fetchAI } from "@/lib/api";

const suggestedPrompts = [
  "Which automotive parts are at risk of stocking out in the next 7 days?",
  "Show me products with the highest revenue at risk across all stores.",
  "Recommend inventory transfers to balance stock levels.",
  "Generate an executive summary of current inventory health.",
  "What are the top 5 overstocked items that need markdown or transfer?",
  "Analyze brake components inventory and identify issues.",
  "Which stores have critical low stock on engine oil and filters?",
  "Show me the aging inventory report for items over 60 days old.",
];

function timestamp() {
  return new Date().toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" });
}

function formatHistoryTime(value: string) {
  return new Date(value).toLocaleString("en-IN", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function createWelcomeMessage(): ChatMessage {
  return {
    id: "initial-ai-welcome",
    role: "assistant",
    text: "Welcome to the AI Inventory Copilot for Automotive Parts. I'm powered by OpenAI and have access to your complete inventory data across 10 warehouses and stores.\n\nI can help you:\n- Analyze stockout risks and revenue at risk\n- Recommend optimal inventory transfers\n- Generate executive summaries and reports\n- Query inventory data using natural language\n- Identify overstock and aging inventory\n\nAsk me anything about your automotive parts inventory!",
    timestamp: timestamp(),
  };
}

async function sendChatMessage(message: string, conversationId?: number): Promise<CopilotResponse> {
  return fetchAI<CopilotResponse>("/api/copilot/chat", {
    method: "POST",
    body: JSON.stringify({ message, conversation_id: conversationId }),
  });
}

async function fetchChatHistory() {
  return fetchAI<{ conversations: ChatHistoryConversation[] }>("/api/copilot/history");
}

export function CopilotPanel() {
  const [messages, setMessages] = useState<ChatMessage[]>([createWelcomeMessage()]);
  const [history, setHistory] = useState<ChatHistoryConversation[]>([]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [conversationId, setConversationId] = useState<number | undefined>();

  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, isTyping]);

  const loadHistory = useCallback(async () => {
    try {
      const data = await fetchChatHistory();
      setHistory(data.conversations);
    } catch {
      setHistory([]);
    }
  }, []);

  useEffect(() => {
    loadHistory();
  }, [loadHistory]);

  function handleNewChat() {
    setConversationId(undefined);
    setMessages([createWelcomeMessage()]);
    setInput("");
  }

  function handleLoadConversation(conversation: ChatHistoryConversation) {
    setConversationId(conversation.conversation_id);
    setMessages(
      conversation.messages.map((message) => ({
        id: `history-${message.id}`,
        role: message.role,
        text: message.content,
        timestamp: formatHistoryTime(message.created_at),
      }))
    );
  }

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
      const aiResponse = await sendChatMessage(trimmed, conversationId);

      if (aiResponse.conversation_id) {
        setConversationId(aiResponse.conversation_id);
      }

      const assistantMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: "assistant",
        text: aiResponse.response,
        timestamp: timestamp(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
      loadHistory();
    } catch (error) {
      const errorMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: "assistant",
        text:
          error instanceof Error
            ? error.message
            : "The AI service is temporarily unavailable. Please check that the backend is running and you're authenticated.",
        timestamp: timestamp(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  }

  return (
    <div className="flex h-full bg-background">
      <aside className="hidden w-72 shrink-0 flex-col border-r border-border bg-white lg:flex">
        <div className="border-b border-border px-4 py-4">
          <div className="flex items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <History className="h-4 w-4 text-primary" />
              <h2 className="text-sm font-semibold text-foreground">Chat History</h2>
            </div>
            <Button type="button" variant="ghost" size="icon" onClick={handleNewChat} title="New chat">
              <Plus className="h-4 w-4" />
            </Button>
          </div>
        </div>

        <div className="flex-1 space-y-2 overflow-y-auto p-3">
          {history.length === 0 ? (
            <p className="px-2 py-3 text-xs text-muted-foreground">No saved conversations yet.</p>
          ) : (
            history.map((conversation) => (
              <button
                key={conversation.conversation_id}
                type="button"
                onClick={() => handleLoadConversation(conversation)}
                className={`w-full rounded-md border px-3 py-2 text-left transition hover:bg-gray-50 ${
                  conversationId === conversation.conversation_id
                    ? "border-primary bg-primary/5"
                    : "border-border bg-white"
                }`}
              >
                <p className="truncate text-sm font-medium text-foreground">
                  {conversation.title || "Untitled conversation"}
                </p>
                <p className="mt-1 text-xs text-muted-foreground">{formatHistoryTime(conversation.updated_at)}</p>
              </button>
            ))
          )}
        </div>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        <div className="border-b border-border bg-white px-8 py-6">
          <div className="flex items-center gap-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary">
              <Sparkles className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-foreground">AI Inventory Copilot</h1>
              <p className="mt-1 text-sm text-muted-foreground">
                Powered by OpenAI + LangGraph. Real-time inventory intelligence from PostgreSQL.
              </p>
            </div>
          </div>
        </div>

        <div className="border-b border-border bg-white px-4 py-3 lg:hidden">
          <div className="mb-2 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <History className="h-4 w-4 text-primary" />
              <span className="text-sm font-semibold text-foreground">Chat History</span>
            </div>
            <Button type="button" variant="ghost" size="sm" onClick={handleNewChat}>
              <Plus className="h-4 w-4" />
              New
            </Button>
          </div>
          {history.length > 0 && (
            <div className="flex gap-2 overflow-x-auto pb-1">
              {history.map((conversation) => (
                <button
                  key={conversation.conversation_id}
                  type="button"
                  onClick={() => handleLoadConversation(conversation)}
                  className={`min-w-44 rounded-md border px-3 py-2 text-left ${
                    conversationId === conversation.conversation_id
                      ? "border-primary bg-primary/5"
                      : "border-border bg-white"
                  }`}
                >
                  <p className="truncate text-xs font-medium text-foreground">
                    {conversation.title || "Untitled conversation"}
                  </p>
                  <p className="mt-1 text-[11px] text-muted-foreground">{formatHistoryTime(conversation.updated_at)}</p>
                </button>
              ))}
            </div>
          )}
        </div>

        <div ref={scrollRef} className="flex-1 overflow-y-auto px-8 py-8">
          <div className="mx-auto max-w-5xl space-y-6">
            {messages.map((message) => (
              <ChatMessageBubble key={message.id} message={message} />
            ))}
            {isTyping && <TypingIndicator />}
            {messages.length === 1 && !conversationId && (
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
                placeholder="Ask the AI copilot..."
                disabled={isTyping}
                className="h-14 flex-1 rounded-xl border border-border bg-background px-5 text-sm outline-none transition focus:ring-2 focus:ring-primary/30 disabled:opacity-50"
              />
              <Button type="submit" size="lg" className="h-14 w-14 rounded-xl" disabled={isTyping}>
                <Send className="h-5 w-5" />
              </Button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}
