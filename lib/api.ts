const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function fetchAnalytics<T>(path: string): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, { cache: "no-store" });

  if (!response.ok) {
    throw new Error(`Analytics API request failed: ${path}`);
  }

  return response.json() as Promise<T>;
}
