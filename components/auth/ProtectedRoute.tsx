"use client";

import { useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { Loader2, Store } from "lucide-react";

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, isAuthenticated, isLoading, logout } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (!isLoading && !isAuthenticated && pathname !== "/login" && pathname !== "/signup") {
      router.push("/login");
    }
  }, [isAuthenticated, isLoading, pathname, router]);

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center bg-background">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!isAuthenticated && pathname !== "/login" && pathname !== "/signup") {
    return null;
  }

  if (
    user?.role === "STORE_MANAGER" &&
    user.assigned_store_id === null &&
    pathname !== "/login" &&
    pathname !== "/signup"
  ) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background px-4">
        <div className="w-full max-w-md rounded-lg border border-border bg-surface p-6 text-center shadow-soft">
          <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-md bg-primary/10 text-primary">
            <Store className="h-6 w-6" />
          </div>
          <h1 className="text-lg font-semibold text-ink">Waiting for store assignment</h1>
          <p className="mt-2 text-sm leading-6 text-ink-muted">
            Your account is connected to {user.realm_name ?? "this realm"}. A Warehouse Owner needs to assign your store before inventory data is shown.
          </p>
          <button
            type="button"
            onClick={() => {
              logout();
              router.push("/login");
            }}
            className="mt-5 rounded-md border border-border px-4 py-2 text-sm font-medium text-ink-muted hover:bg-gray-50 hover:text-ink"
          >
            Sign out
          </button>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}
