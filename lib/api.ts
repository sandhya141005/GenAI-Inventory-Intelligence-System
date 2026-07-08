const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

function getAuthHeaders(): HeadersInit {
  if (typeof window === "undefined") return {};
  const token = localStorage.getItem("access_token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function fetchAnalytics<T>(path: string): Promise<T> {
  console.log("Calling API:", `${API_URL}${path}`);
  const response = await fetch(`${API_URL}${path}`, {
    cache: "no-store",
    headers: getAuthHeaders(),
  });

 if (!response.ok) {
  if (response.status === 401 && typeof window !== "undefined") {
    window.location.href = "/login";
    throw new Error("Unauthorized");
  }
  const errorText = await response.text();

  console.log("API FAILED");
  console.log("STATUS:", response.status);
  console.log("BODY:", errorText);

  throw new Error(`Analytics API request failed: ${path}`);
}

  return response.json() as Promise<T>;
}

export async function fetchAI<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...getAuthHeaders(),
      ...options?.headers,
    },
  });

  if (!response.ok) {
    if (response.status === 401 && typeof window !== "undefined") {
      window.location.href = "/login";
      throw new Error("Unauthorized");
    }
    const error = await response.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(error.detail || `AI API request failed: ${path}`);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}
