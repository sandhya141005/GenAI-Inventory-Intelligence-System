"use client";

import { Sidebar } from "./Sidebar";
import { CopilotPanel } from "./CopilotPanel";
import { MobileNav } from "./MobileNav";

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-screen w-full overflow-hidden bg-background">
      <Sidebar />

      <main className="flex-1 overflow-y-auto scrollbar-thin pb-16 md:pb-0">
        {children}
      </main>

      {/* <CopilotPanel/> */}
      <MobileNav />
    </div>
  );
}
