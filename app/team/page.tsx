"use client";

import { useEffect, useState } from "react";
import { Copy, RefreshCw, Trash2, Users } from "lucide-react";
import { Button } from "@/components/ui/button";
import { fetchAI } from "@/lib/api";

interface StoreOption {
  id: number;
  name: string | null;
  city: string | null;
  region: string | null;
}

interface Manager {
  id: number;
  full_name: string | null;
  email: string;
  assigned_store_id: number | null;
  assigned_store_name: string | null;
  created_at: string | null;
}

interface RealmSettings {
  realm: {
    id: number;
    name: string;
    industry_tag: string;
    join_code: string;
    created_at: string | null;
  };
  stores: StoreOption[];
  managers: Manager[];
}

export default function TeamPage() {
  const [data, setData] = useState<RealmSettings | null>(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  async function loadSettings() {
    setIsLoading(true);
    try {
      setData(await fetchAI<RealmSettings>("/api/realm/settings"));
      setError("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load team settings");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    loadSettings();
  }, []);

  async function assignStore(managerId: number, storeId: string) {
    await fetchAI(`/api/realm/managers/${managerId}/store`, {
      method: "PATCH",
      body: JSON.stringify({ store_id: storeId ? Number(storeId) : null }),
    });
    await loadSettings();
  }

  async function removeManager(managerId: number) {
    await fetchAI(`/api/realm/managers/${managerId}`, { method: "DELETE" });
    await loadSettings();
  }

  async function regenerateCode() {
    const response = await fetchAI<{ join_code: string }>("/api/realm/regenerate-code", { method: "POST" });
    setData((current) => current && { ...current, realm: { ...current.realm, join_code: response.join_code } });
  }

  return (
    <div className="mx-auto max-w-5xl px-6 py-8 space-y-6">
      <div>
        <h1 className="text-lg font-semibold text-ink">Team</h1>
        <p className="mt-1 text-sm text-ink-muted">Manage realm access and store assignments.</p>
      </div>

      {error && <div className="rounded-md bg-danger/10 px-4 py-3 text-sm text-danger">{error}</div>}
      {isLoading && <div className="rounded-md border border-border bg-surface p-5 text-sm text-ink-muted">Loading team settings...</div>}

      {data && (
        <>
          <section className="rounded-lg border border-border bg-surface p-5 shadow-soft">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p className="text-sm font-semibold text-ink">{data.realm.name}</p>
                <p className="mt-1 text-xs text-ink-muted">{data.realm.industry_tag}</p>
              </div>
              <div className="flex flex-wrap items-center gap-2">
                <div className="rounded-md border border-border bg-background px-4 py-2">
                  <p className="text-xs uppercase tracking-wide text-ink-muted">Join Code</p>
                  <p className="text-2xl font-semibold tracking-[0.3em] text-ink">{data.realm.join_code}</p>
                </div>
                <Button type="button" variant="secondary" onClick={() => navigator.clipboard?.writeText(data.realm.join_code)}>
                  <Copy className="h-4 w-4" />
                  Copy
                </Button>
                <Button type="button" variant="secondary" onClick={regenerateCode}>
                  <RefreshCw className="h-4 w-4" />
                  Regenerate
                </Button>
              </div>
            </div>
          </section>

          <section className="rounded-lg border border-border bg-surface shadow-soft">
            <div className="flex items-center gap-2 border-b border-border px-5 py-4">
              <Users className="h-4 w-4 text-primary" />
              <h2 className="text-sm font-semibold text-ink">Store Managers</h2>
            </div>
            <div className="divide-y divide-border">
              {data.managers.length === 0 && <p className="px-5 py-6 text-sm text-ink-muted">No store managers have joined yet.</p>}
              {data.managers.map((manager) => (
                <div key={manager.id} className="grid gap-3 px-5 py-4 md:grid-cols-[1fr_220px_auto] md:items-center">
                  <div>
                    <p className="text-sm font-medium text-ink">{manager.full_name ?? "Unnamed manager"}</p>
                    <p className="text-xs text-ink-muted">{manager.email}</p>
                    <p className="mt-1 text-xs text-ink-muted">
                      Joined {manager.created_at ? new Date(manager.created_at).toLocaleDateString() : "recently"}
                    </p>
                  </div>
                  <select
                    value={manager.assigned_store_id ?? ""}
                    onChange={(event) => assignStore(manager.id, event.target.value)}
                    className="h-9 rounded-md border border-border bg-background px-3 text-sm outline-none focus:ring-2 focus:ring-primary/30"
                  >
                    <option value="">Unassigned</option>
                    {data.stores.map((store) => (
                      <option key={store.id} value={store.id}>
                        {store.name ?? `Store ${store.id}`}
                      </option>
                    ))}
                  </select>
                  <Button type="button" variant="danger" size="sm" onClick={() => removeManager(manager.id)}>
                    <Trash2 className="h-4 w-4" />
                    Remove
                  </Button>
                </div>
              ))}
            </div>
          </section>
        </>
      )}
    </div>
  );
}
