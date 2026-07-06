"use client";

import { usePathname } from "next/navigation";
import { Sidebar } from "./Sidebar";
import { CopilotPanel } from "./CopilotPanel";
import { MobileNav } from "./MobileNav";
import { useAuth } from "@/lib/auth-context";

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { isAuthenticated } = useAuth();
  
  const isAuthPage = pathname === "/login" || pathname === "/signup";

  if (isAuthPage) {
    return <>{children}</>;
  }

  if (!isAuthenticated) {
    return <>{children}</>;
  }

  return (
    <div className="flex h-screen w-full overflow-hidden bg-background">
      <Sidebar />

      <main className="flex-1 overflow-y-auto scrollbar-thin pb-16 md:pb-0">
        {children}
      </main>

      <MobileNav />
    </div>
  );
}
