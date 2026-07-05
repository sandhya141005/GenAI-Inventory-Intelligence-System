import { Sparkles, User } from "lucide-react";
import { ChatMessage as ChatMessageType } from "@/lib/types";
import { InsightCard } from "./InsightCard";
import { cn } from "@/lib/utils";

export function ChatMessageBubble({ message }: { message: ChatMessageType }) {
  const isAssistant = message.role === "assistant";

  return (
    <div
      className={cn(
        "flex gap-3 animate-fade-in",
        !isAssistant && "flex-row-reverse"
      )}
    >
      <div
        className={cn(
          "h-7 w-7 shrink-0 rounded-full flex items-center justify-center",
          isAssistant ? "bg-primary" : "bg-gray-200"
        )}
      >
        {isAssistant ? (
          <Sparkles className="h-3.5 w-3.5 text-white" />
        ) : (
          <User className="h-3.5 w-3.5 text-ink-muted" />
        )}
      </div>

      <div className={cn("max-w-[85%]", !isAssistant && "text-right")}>
        <div
          className={cn(
            "inline-block rounded-lg px-4 py-2.5 text-sm leading-relaxed",
            isAssistant
              ? "bg-white border border-border text-ink"
              : "bg-primary text-white"
          )}
        >
          {message.text}
        </div>

        {message.insight && (
          <div className="text-left">
            <InsightCard insight={message.insight} />
          </div>
        )}

        <p className="mt-1 text-[11px] text-ink-muted">{message.timestamp}</p>
      </div>
    </div>
  );
}

export function TypingIndicator() {
  return (
    <div className="flex gap-3 animate-fade-in">
      <div className="h-7 w-7 shrink-0 rounded-full bg-primary flex items-center justify-center">
        <Sparkles className="h-3.5 w-3.5 text-white" />
      </div>
      <div className="inline-flex items-center gap-1 rounded-lg border border-border bg-white px-4 py-3">
        <span className="h-1.5 w-1.5 rounded-full bg-ink-muted animate-typing-dot [animation-delay:0ms]" />
        <span className="h-1.5 w-1.5 rounded-full bg-ink-muted animate-typing-dot [animation-delay:150ms]" />
        <span className="h-1.5 w-1.5 rounded-full bg-ink-muted animate-typing-dot [animation-delay:300ms]" />
      </div>
    </div>
  );
}
