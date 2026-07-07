import { CopilotPanel } from "@/components/layout/CopilotPanel";

export default function RecommendationsPage() {
  return (
    <div className="flex h-[calc(100vh-64px)]">
      {/* Sidebar stays outside */}

      <main className="flex-1 overflow-hidden">
        <CopilotPanel />
      </main>
    </div>
  );
}