"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
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
  Settings,
} from "lucide-react";
import { cn } from "@/lib/utils";

const navItems = [
  { href: "/overview", label: "Overview", icon: LayoutGrid },
  { href: "/", label: "Decision Engine", icon: Sparkles, isSame: true, hideIfHome: true },
  { href: "/inventory", label: "Inventory", icon: Package },
  { href: "/recommendations", label: "Recommendations", icon: ListChecks },
  { href: "/reports", label: "Reports", icon: FileText },
  { href: "/analytics", label: "Analytics", icon: BarChart3 },
  { href: "/transfers", label: "Transfers", icon: ArrowLeftRight },
  { href: "/aging", label: "Inventory Aging", icon: Clock },
  { href: "/notices", label: "Notice Board", icon: Bell },
  { href: "/settings", label: "Settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="hidden md:flex w-[220px] shrink-0 flex-col border-r border-border bg-surface">
      <div className="flex items-center gap-2 px-5 h-16 border-b border-border">
        <div className="h-7 w-7 rounded-md bg-primary flex items-center justify-center">
          <Sparkles className="h-4 w-4 text-white" />
        </div>
        <span className="text-sm font-semibold text-ink tracking-tight">
          Inventory IQ
        </span>
      </div>

      <nav className="flex-1 px-3 py-4 space-y-0.5">
        {navItems
          .filter((item) => !item.hideIfHome)
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
      </nav>

      <div className="p-3 border-t border-border">
        <div className="flex items-center gap-2 rounded-md px-3 py-2 bg-gray-50">
          <div className="h-7 w-7 rounded-full bg-primary/15 flex items-center justify-center text-xs font-semibold text-primary">
            RM
          </div>
          <div className="text-xs leading-tight">
            <p className="font-medium text-ink">R. Mehta</p>
            <p className="text-ink-muted">Regional Ops Lead</p>
          </div>
        </div>
      </div>
    </aside>
  );
}
