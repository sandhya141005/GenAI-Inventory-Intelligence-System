"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutGrid, Sparkles, Package, ListChecks, FileText, Shield } from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuth } from "@/lib/auth-context";

const items = [
  { href: "/overview", label: "Overview", icon: LayoutGrid },
  { href: "/copilot", label: "Copilot", icon: Sparkles },
  { href: "/inventory", label: "Inventory", icon: Package },
  { href: "/recommendations", label: "Actions", icon: ListChecks },
  { href: "/reports", label: "Reports", icon: FileText },
  { href: "/team", label: "Team", icon: Shield, ownerOnly: true },
];

export function MobileNav() {
  const pathname = usePathname();
  const { user } = useAuth();

  return (
    <nav className="md:hidden fixed bottom-0 inset-x-0 z-20 flex items-center justify-around border-t border-border bg-surface h-16">
      {items
        .filter((item) => !item.ownerOnly || user?.role === "WAREHOUSE_OWNER")
        .map((item) => {
        const active = pathname === item.href;
        const Icon = item.icon;
        return (
          <Link
            key={item.href}
            href={item.href}
            className={cn(
              "flex flex-col items-center gap-1 text-[11px]",
              active ? "text-primary" : "text-ink-muted"
            )}
          >
            <Icon className="h-5 w-5" strokeWidth={1.8} />
            {item.label}
          </Link>
        );
      })}
    </nav>
  );
}
