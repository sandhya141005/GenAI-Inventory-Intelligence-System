import { Sparkles, User } from "lucide-react";
import { ChatMessage as ChatMessageType } from "@/lib/types";
import { InsightCard } from "./InsightCard";
import { cn } from "@/lib/utils";

function renderInlineMarkdown(text: string) {
  return text.split(/(\*\*[^*]+\*\*)/g).map((part, index) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return <strong key={index}>{part.slice(2, -2)}</strong>;
    }

    return part;
  });
}

function normalizeMarkdown(text: string) {
  return text
    .replace(/\s+(#{2,6}\s+)/g, "\n$1")
    .replace(/\s+-\s+(\*\*)/g, "\n- $1")
    .trim();
}

function MarkdownMessage({ text }: { text: string }) {
  const lines = normalizeMarkdown(text).split(/\r?\n/);
  const blocks: React.ReactNode[] = [];
  let index = 0;

  while (index < lines.length) {
    const line = lines[index].trim();

    if (!line) {
      index += 1;
      continue;
    }

    // Handle code blocks
    if (line.startsWith("```")) {
      const lang = line.slice(3).trim();
      const codeLines: string[] = [];
      index += 1;
      
      while (index < lines.length && !lines[index].trim().startsWith("```")) {
        codeLines.push(lines[index]);
        index += 1;
      }
      
      if (index < lines.length) {
        index += 1; // Skip closing ```
      }
      
      blocks.push(
        <pre key={index} className="my-3 overflow-x-auto rounded-md bg-gray-900 p-3">
          <code className="text-xs text-gray-100 font-mono whitespace-pre">
            {codeLines.join("\n")}
          </code>
        </pre>
      );
      continue;
    }

    const heading = line.match(/^(#{1,6})\s+(.+)$/);
    if (heading) {
      const level = heading[1].length;
      const className =
        level <= 3
          ? "mt-3 first:mt-0 text-base font-semibold text-ink"
          : "mt-2 text-sm font-semibold text-ink";

      blocks.push(
        <p key={index} className={className}>
          {renderInlineMarkdown(heading[2].replace(/\s*#+$/, ""))}
        </p>
      );
      index += 1;
      continue;
    }

    if (line.startsWith("|") && lines[index + 1]?.trim().match(/^\|?[\s:-]+\|/)) {
      const tableLines: string[] = [];
      while (lines[index]?.trim().startsWith("|")) {
        tableLines.push(lines[index].trim());
        index += 1;
      }

      const [headerLine, , ...bodyLines] = tableLines;
      const headers = headerLine.split("|").map((cell) => cell.trim()).filter(Boolean);
      const rows = bodyLines.map((row) =>
        row.split("|").map((cell) => cell.trim()).filter(Boolean)
      );

      blocks.push(
        <div key={index} className="my-3 overflow-x-auto">
          <table className="min-w-full border-collapse text-left text-xs">
            <thead>
              <tr>
                {headers.map((header) => (
                  <th key={header} className="border border-border bg-gray-50 px-2 py-1 font-semibold">
                    {renderInlineMarkdown(header)}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((row, rowIndex) => (
                <tr key={rowIndex}>
                  {row.map((cell, cellIndex) => (
                    <td key={cellIndex} className="border border-border px-2 py-1 align-top">
                      {renderInlineMarkdown(cell)}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );
      continue;
    }

    if (line.startsWith("- ")) {
      const items: string[] = [];
      while (lines[index]?.trim().startsWith("- ")) {
        items.push(lines[index].trim().slice(2));
        index += 1;
      }

      blocks.push(
        <ul key={index} className="my-2 list-disc space-y-1 pl-5">
          {items.map((item, itemIndex) => (
            <li key={itemIndex}>{renderInlineMarkdown(item)}</li>
          ))}
        </ul>
      );
      continue;
    }

    const paragraph: string[] = [];
    while (
      index < lines.length &&
      lines[index].trim() &&
      !lines[index].trim().match(/^(#{1,6})\s+/) &&
      !lines[index].trim().startsWith("- ") &&
      !lines[index].trim().startsWith("|") &&
      !lines[index].trim().startsWith("```")
    ) {
      paragraph.push(lines[index].trim());
      index += 1;
    }

    blocks.push(
      <p key={index} className="my-2 first:mt-0 last:mb-0">
        {renderInlineMarkdown(paragraph.join(" "))}
      </p>
    );
  }

  return <div className="space-y-2 text-left">{blocks}</div>;
}

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
          {isAssistant ? <MarkdownMessage text={message.text} /> : message.text}
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
