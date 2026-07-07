"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  LayoutGrid,
  Sparkles,
  Package,
  ListChecks,
  FileText,
  BarChart3,
  ArrowLeftRight,
  Clock,
  Bell,
  HandHeart,
  Settings,
  Shield,
  LogOut,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuth } from "@/lib/auth-context";

const navItems = [
  { href: "/overview", label: "Overview", icon: LayoutGrid },
  { href: "/", label: "AI Copilot", icon: Sparkles, isSame: true, hideIfHome: true },
  { href: "/inventory", label: "Inventory", icon: Package },
  { href: "/recommendations", label: "Recommendations", icon: ListChecks },
  { href: "/reports", label: "Reports", icon: FileText },
  { href: "/analytics", label: "Analytics", icon: BarChart3 },
  { href: "/transfers", label: "Transfers", icon: ArrowLeftRight },
  { href: "/aging", label: "Inventory Aging", icon: Clock },
  { href: "/notices", label: "Notice Board", icon: Bell },
  { href: "/donations", label: "Donation History", icon: HandHeart },
  { href: "/settings", label: "Settings", icon: Settings },
];

const aiReportItems = [
  { href: "/ai-reports/morning-brief", label: "Morning Brief" },
  { href: "/ai-reports/weekly-report", label: "Weekly Report" },
  { href: "/ai-reports/executive-summary", label: "Executive Summary" },
];

export function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const { user, logout } = useAuth();

  function handleLogout() {
    logout();
    router.push("/login");
  }

  return (
    <aside className="hidden md:flex w-[220px] shrink-0 flex-col border-r border-border bg-surface">
      <Link href="/" className="flex items-center gap-2 px-5 h-16 border-b border-border">
        <img src="/stocklens-icon.png" alt="StockLens" className="h-7 w-7 rounded-md object-cover" />
        <span className="text-sm font-semibold text-ink tracking-tight">
          StockLens
        </span>
      </Link>

      <div className="flex-1 overflow-y-auto">
        <nav className="px-3 py-4 space-y-0.5">
          {navItems
            .filter((item) => !item.hideIfHome)
            .filter((item) => item.href !== "/settings" || user?.role === "WAREHOUSE_OWNER")
            .map((item) => {
              const active = pathname === item.href;
              const Icon = item.icon;
              return (
                <Link
                  key={item.label}
                  href={item.href}
                  className={cn(
                    "flex items-center gap-3 rounded-md px-3 py-2 text-sm transition-colors",
                    active
                      ? "bg-primary/8 text-primary font-medium"
                      : "text-ink-muted hover:bg-gray-50 hover:text-ink"
                  )}
                >
                  <Icon
                    className={cn(
                      "h-4 w-4",
                      active ? "text-primary" : "text-ink-muted"
                    )}
                    strokeWidth={1.8}
                  />
                  {item.label}
                </Link>
              );
            })}
          {user?.role === "WAREHOUSE_OWNER" && (
            <Link
              href="/team"
              className={cn(
                "flex items-center gap-3 rounded-md px-3 py-2 text-sm transition-colors",
                pathname === "/team"
                  ? "bg-primary/8 text-primary font-medium"
                  : "text-ink-muted hover:bg-gray-50 hover:text-ink"
              )}
            >
              <Shield className={cn("h-4 w-4", pathname === "/team" ? "text-primary" : "text-ink-muted")} strokeWidth={1.8} />
              Team
            </Link>
          )}
        </nav>

        <div className="px-3 pb-4">
          <div className="pt-3 mt-3 border-t border-border">
            <p className="px-3 pb-2 text-xs font-semibold text-ink-muted uppercase tracking-wide">
              AI Reports
            </p>
            {aiReportItems.map((item) => {
              const active = pathname === item.href;
              return (
                <Link
                  key={item.label}
                  href={item.href}
                  className={cn(
                    "flex items-center gap-3 rounded-md px-3 py-2 text-sm transition-colors pl-10",
                    active
                      ? "bg-primary/8 text-primary font-medium"
                      : "text-ink-muted hover:bg-gray-50 hover:text-ink"
                  )}
                >
                  {item.label}
                </Link>
              );
            })}
          </div>
        </div>
      </div>

      <div className="p-3 border-t border-border space-y-2">
        <div className="rounded-md border border-border bg-background px-3 py-2 text-xs leading-5">
          <p className="font-medium text-ink">
            {user?.role === "STORE_MANAGER"
              ? `Viewing: ${user.assigned_store_name ?? "Unassigned"}`
              : "Viewing: All Stores"}
          </p>
          <p className="truncate text-ink-muted">{user?.realm_name ?? "No realm"}</p>
        </div>
        <div className="flex items-center gap-2 rounded-md px-3 py-2 bg-gray-50">
          <div className="h-7 w-7 rounded-full bg-primary/15 flex items-center justify-center text-xs font-semibold text-primary">
            {user?.full_name?.charAt(0).toUpperCase() || "U"}
          </div>
          <div className="text-xs leading-tight flex-1 min-w-0">
            <p className="font-medium text-ink truncate">{user?.full_name || "User"}</p>
            <p className="text-ink-muted truncate">{user?.email || "user@example.com"}</p>
          </div>
        </div>
        <button
          onClick={handleLogout}
          className="flex items-center gap-3 rounded-md px-3 py-2 text-sm text-ink-muted hover:bg-gray-50 hover:text-ink transition-colors w-full"
        >
          <LogOut className="h-4 w-4" strokeWidth={1.8} />
          Sign Out
        </button>
      </div>
    </aside>
  );
}
