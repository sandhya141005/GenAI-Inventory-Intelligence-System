"use client";

import type React from "react";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Building2, Check, DoorOpen, Sparkles, Users } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/lib/auth-context";
import { cn } from "@/lib/utils";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export default function SignupPage() {
  const [step, setStep] = useState(1);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [companyName, setCompanyName] = useState("");
  const [industryTag, setIndustryTag] = useState("");
  const [realmAction, setRealmAction] = useState<"create" | "join">("create");
  const [joinCode, setJoinCode] = useState("");
  const [industryTags, setIndustryTags] = useState<string[]>([]);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const { signup } = useAuth();
  const router = useRouter();

  useEffect(() => {
    fetch(`${API_URL}/api/auth/industry-tags`)
      .then((response) => response.json())
      .then((data) => {
        setIndustryTags(data.tags ?? []);
        setIndustryTag(data.tags?.[0] ?? "");
      })
      .catch(() => {
        setIndustryTags(["Automotive Parts", "Retail", "Groceries"]);
        setIndustryTag("Automotive Parts");
      });
  }, []);

  function nextStep() {
    setError("");
    if (step === 1 && (!fullName || !email || password.length < 8)) {
      setError("Add your name, email, and a password with at least 8 characters.");
      return;
    }
    if (step === 2 && (!companyName || !industryTag)) {
      setError("Add your company name and choose an industry.");
      return;
    }
    setStep((current) => Math.min(3, current + 1));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    if (realmAction === "join" && joinCode.trim().length !== 4) {
      setError("Enter the 4-digit realm code from your Warehouse Owner.");
      return;
    }
    setIsLoading(true);

    try {
      await signup({
        email,
        password,
        full_name: fullName,
        company_name: companyName,
        industry_tag: industryTag,
        realm_action: realmAction,
        join_code: realmAction === "join" ? joinCode.trim() : undefined,
      });
      router.push("/overview");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Signup failed");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-background px-4 py-8">
      <div className="mx-auto w-full max-w-2xl space-y-6 rounded-lg border border-border bg-surface p-6 shadow-soft">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary">
            <Sparkles className="h-5 w-5 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-ink">Create your StockLens account</h1>
            <p className="text-sm text-ink-muted">Set up your workspace access</p>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-2">
          {[1, 2, 3].map((item) => (
            <div key={item} className="flex items-center gap-2">
              <div className={cn("h-2 flex-1 rounded-full", step >= item ? "bg-primary" : "bg-gray-200")} />
              {step > item && <Check className="h-4 w-4 text-primary" />}
            </div>
          ))}
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          {step === 1 && (
            <div className="grid gap-4">
              <Field label="Full Name" value={fullName} onChange={setFullName} placeholder="John Doe" />
              <Field label="Email" type="email" value={email} onChange={setEmail} placeholder="you@example.com" />
              <Field label="Password" type="password" value={password} onChange={setPassword} placeholder="Minimum 8 characters" />
            </div>
          )}

          {step === 2 && (
            <div className="grid gap-4">
              <Field label="Company Name" value={companyName} onChange={setCompanyName} placeholder="Digital Dumplings Inc." />
              <div>
                <label className="mb-1 block text-sm font-medium text-ink">Industry / Domain</label>
                <select
                  value={industryTag}
                  onChange={(e) => setIndustryTag(e.target.value)}
                  className="w-full rounded-md border border-border bg-background px-4 py-2.5 text-sm outline-none transition focus:ring-2 focus:ring-primary/30"
                >
                  {industryTags.map((tag) => (
                    <option key={tag} value={tag}>
                      {tag}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          )}

          {step === 3 && (
            <div className="space-y-4">
              <div className="grid gap-3 sm:grid-cols-2">
                <OptionCard
                  active={realmAction === "create"}
                  icon={<Building2 className="h-5 w-5" />}
                  title="Create a Realm"
                  detail="Start a company workspace and become the Warehouse Owner."
                  onClick={() => setRealmAction("create")}
                />
                <OptionCard
                  active={realmAction === "join"}
                  icon={<Users className="h-5 w-5" />}
                  title="Join a Realm"
                  detail="Use the 4-digit code from your Warehouse Owner."
                  onClick={() => setRealmAction("join")}
                />
              </div>

              {realmAction === "join" && (
                <div>
                  <label className="mb-1 block text-sm font-medium text-ink">Realm Code</label>
                  <div className="relative">
                    <DoorOpen className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-ink-muted" />
                    <input
                      value={joinCode}
                      onChange={(e) => setJoinCode(e.target.value.replace(/\D/g, "").slice(0, 4))}
                      required
                      className="w-full rounded-md border border-border bg-background py-2.5 pl-10 pr-4 text-sm tracking-[0.4em] outline-none transition focus:ring-2 focus:ring-primary/30"
                      placeholder="8341"
                    />
                  </div>
                </div>
              )}
            </div>
          )}

          {error && <div className="rounded-md bg-danger/10 px-4 py-2.5 text-sm text-danger">{error}</div>}

          <div className="flex items-center justify-between gap-3">
            <Button type="button" variant="secondary" disabled={step === 1 || isLoading} onClick={() => setStep((current) => current - 1)}>
              Back
            </Button>
            {step < 3 ? (
              <Button type="button" onClick={nextStep}>
                Continue
              </Button>
            ) : (
              <Button type="submit" disabled={isLoading}>
                {isLoading ? "Creating account..." : "Finish Signup"}
              </Button>
            )}
          </div>
        </form>

        <p className="text-center text-sm text-ink-muted">
          Already have an account?{" "}
          <a href="/login" className="font-medium text-primary hover:underline">
            Sign in
          </a>
        </p>
      </div>
    </div>
  );
}

function Field({
  label,
  value,
  onChange,
  placeholder,
  type = "text",
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  placeholder: string;
  type?: string;
}) {
  return (
    <div>
      <label className="mb-1 block text-sm font-medium text-ink">{label}</label>
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        required
        minLength={type === "password" ? 8 : undefined}
        className="w-full rounded-md border border-border bg-background px-4 py-2.5 text-sm outline-none transition focus:ring-2 focus:ring-primary/30"
        placeholder={placeholder}
      />
    </div>
  );
}

function OptionCard({
  active,
  icon,
  title,
  detail,
  onClick,
}: {
  active: boolean;
  icon: React.ReactNode;
  title: string;
  detail: string;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        "rounded-md border p-4 text-left transition",
        active ? "border-primary bg-primary/5 text-ink" : "border-border bg-background text-ink-muted hover:border-primary/50"
      )}
    >
      <div className="mb-3 flex h-9 w-9 items-center justify-center rounded-md bg-white text-primary shadow-soft">{icon}</div>
      <p className="text-sm font-semibold text-ink">{title}</p>
      <p className="mt-1 text-xs leading-5 text-ink-muted">{detail}</p>
    </button>
  );
}
