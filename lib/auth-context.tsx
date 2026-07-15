"use client";

import { createContext, useContext, useEffect, useState, ReactNode } from "react";

interface User {
  id: number;
  email: string;
  full_name: string;
  is_active: boolean;
  realm_id: number | null;
  role: "WAREHOUSE_OWNER" | "STORE_MANAGER" | null;
  assigned_store_id: number | null;
  assigned_store_name: string | null;
  realm_name: string | null;
  industry_tag: string | null;
}

interface AuthTokens {
  access_token: string;
  refresh_token: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (payload: SignupPayload) => Promise<void>;
  logout: () => void;
}

export interface SignupPayload {
  email: string;
  password: string;
  full_name: string;
  company_name?: string;
  industry_tag?: string;
  realm_action: "create" | "join";
  join_code?: string;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

function getTokens(): AuthTokens | null {
  if (typeof window === "undefined") return null;
  const access = localStorage.getItem("access_token");
  const refresh = localStorage.getItem("refresh_token");
  if (!access || !refresh) return null;
  return { access_token: access, refresh_token: refresh };
}

function setTokens(tokens: AuthTokens) {
  localStorage.setItem("access_token", tokens.access_token);
  localStorage.setItem("refresh_token", tokens.refresh_token);
}

function clearTokens() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
}

async function parseApiError(response: Response, fallback: string): Promise<string> {
  const data = await response.json().catch(() => null);
  const detail = data?.detail ?? data?.message ?? fallback;
  if (Array.isArray(detail)) {
    return detail.map((item) => item?.msg ?? item?.message ?? JSON.stringify(item)).join(", ");
  }
  if (detail && typeof detail === "object") {
    return detail.msg ?? detail.message ?? JSON.stringify(detail);
  }
  return String(detail);
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  async function fetchCurrentUser(accessToken: string): Promise<User | null> {
    try {
      const response = await fetch(`${API_URL}/api/auth/me`, {
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      if (!response.ok) return null;
      return await response.json();
    } catch {
      return null;
    }
  }

  async function refreshAccessToken(refreshToken: string): Promise<AuthTokens | null> {
    try {
      const response = await fetch(`${API_URL}/api/auth/refresh`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });
      if (!response.ok) return null;
      return await response.json();
    } catch {
      return null;
    }
  }

  useEffect(() => {
    async function initAuth() {
      const tokens = getTokens();
      if (!tokens) {
        setIsLoading(false);
        return;
      }

      let currentUser = await fetchCurrentUser(tokens.access_token);
      if (!currentUser) {
        const newTokens = await refreshAccessToken(tokens.refresh_token);
        if (newTokens) {
          setTokens(newTokens);
          currentUser = await fetchCurrentUser(newTokens.access_token);
        }
      }

      setUser(currentUser);
      setIsLoading(false);
    }

    initAuth();
  }, []);

  async function login(email: string, password: string) {
    const response = await fetch(`${API_URL}/api/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
      throw new Error(await parseApiError(response, "Login failed"));
    }

    const tokens: AuthTokens = await response.json();
    setTokens(tokens);

    const currentUser = await fetchCurrentUser(tokens.access_token);
    setUser(currentUser);
  }

  async function signup(payload: SignupPayload) {
    const response = await fetch(`${API_URL}/api/auth/signup`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      throw new Error(await parseApiError(response, "Signup failed"));
    }

    await login(payload.email, payload.password);
  }

  function logout() {
    clearTokens();
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, isAuthenticated: !!user, isLoading, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}

export async function getAuthToken(): Promise<string | null> {
  const tokens = getTokens();
  return tokens?.access_token ?? null;
}
