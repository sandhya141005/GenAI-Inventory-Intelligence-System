"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutGrid, Sparkles, Package, ListChecks, FileText } from "lucide-react";
import { cn } from "@/lib/utils";

const items = [
  { href: "/", label: "Overview", icon: LayoutGrid },
  { href: "/copilot", label: "Engine", icon: Sparkles },
  { href: "/inventory", label: "Inventory", icon: Package },
  { href: "/recommendations", label: "Actions", icon: ListChecks },
  { href: "/reports", label: "Reports", icon: FileText },
];

export function MobileNav() {
  const pathname = usePathname();

  return (
    <nav className="md:hidden fixed bottom-0 inset-x-0 z-20 flex items-center justify-around border-t border-border bg-surface h-16">
      {items.map((item) => {
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
