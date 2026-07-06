import type { Metadata } from "next";
import "./globals.css";
import { AppShell } from "@/components/layout/AppShell";
import { AuthProvider } from "@/lib/auth-context";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";

export const metadata: Metadata = {
  title: "Inventory Decision Intelligence",
  description: "PostgreSQL-backed inventory decision intelligence for enterprise retail.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>
          <ProtectedRoute>
            <AppShell>{children}</AppShell>
          </ProtectedRoute>
        </AuthProvider>
      </body>
    </html>
  );
}
