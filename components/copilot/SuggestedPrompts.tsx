import { ArrowUpRight } from "lucide-react";

export function SuggestedPrompts({
  prompts,
  onSelect,
}: {
  prompts: string[];
  onSelect: (prompt: string) => void;
}) {
  return (
    <div className="grid grid-cols-1 gap-2">
      {prompts.map((prompt) => (
        <button
          key={prompt}
          onClick={() => onSelect(prompt)}
          className="group flex items-center justify-between rounded-md border border-border bg-white px-3.5 py-2.5 text-left text-sm text-ink hover:border-accent/40 hover:bg-accent/5 transition-colors"
        >
          <span>{prompt}</span>
          <ArrowUpRight className="h-3.5 w-3.5 text-ink-muted opacity-0 group-hover:opacity-100 transition-opacity shrink-0 ml-2" />
        </button>
      ))}
    </div>
  );
}
