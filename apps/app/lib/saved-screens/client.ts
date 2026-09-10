import type { AccessTokenProvider, SavedScreen, ScreenRunPage } from "./types";
import type { ScreenQueryPayload } from "@/lib/screener/types";
import { createClient } from "@/lib/supabase/client";

/** Access tokens are forwarded only to the app's user-scoped saved-screen API. */
export const browserAccessToken: AccessTokenProvider = async () => {
  if (typeof window === "undefined") return null;
  try {
    const { data } = await createClient().auth.getSession();
    return data.session?.access_token || null;
  } catch {
    return null;
  }
};

async function request<T>(path: string, tokenProvider: AccessTokenProvider, init?: RequestInit): Promise<T> {
  const token = await tokenProvider();
  if (!token) throw new Error("Sign in to manage saved screens.");
  const response = await fetch(path, {
    ...init,
    headers: {
      accept: "application/json",
      authorization: `Bearer ${token}`,
      ...(init?.body ? { "content-type": "application/json" } : {}),
      ...init?.headers,
    },
  });
  const payload: unknown = await response.json().catch(() => null);
  if (!response.ok) {
    const detail = payload && typeof payload === "object" && "detail" in payload
      ? String((payload as { detail: unknown }).detail)
      : "Saved screens could not be updated.";
    throw new Error(response.status === 401 ? "Your session has expired. Sign in again." : detail);
  }
  return payload as T;
}

async function sessionRequest<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    ...init,
    headers: { accept: "application/json", ...(init?.body ? { "content-type": "application/json" } : {}), ...init?.headers },
  });
  const payload: unknown = await response.json().catch(() => null);
  if (!response.ok) {
    const detail = payload && typeof payload === "object" && "detail" in payload
      ? String((payload as { detail: unknown }).detail)
      : "The screen could not be loaded.";
    throw new Error(detail);
  }
  return payload as T;
}

export const savedScreensApi = {
  list: (tokens: AccessTokenProvider = browserAccessToken) => request<SavedScreen[]>("/api/screens", tokens),
  create: (name: string, query: ScreenQueryPayload, runId?: string, tokens: AccessTokenProvider = browserAccessToken) =>
    request<{ id: number; name: string; slug: string }>("/api/screens", tokens, { method: "POST", body: JSON.stringify({ name, query, run_id: runId || null }) }),
  get: (slug: string, cursor?: string, tokens: AccessTokenProvider = browserAccessToken) =>
    request<SavedScreen>(`/api/screens/${encodeURIComponent(slug)}${cursor ? `?cursor=${encodeURIComponent(cursor)}` : ""}`, tokens),
  createRun: (text: string) =>
    sessionRequest<ScreenRunPage | Record<string, unknown>>("/api/screen-runs", { method: "POST", body: JSON.stringify({ text, page_size: 50 }) }),
  getRun: (id: string, cursor?: string) =>
    sessionRequest<ScreenRunPage>(`/api/screen-runs/${id}${cursor ? `?cursor=${encodeURIComponent(cursor)}` : ""}`),
  refresh: (slug: string, tokens: AccessTokenProvider = browserAccessToken) =>
    request<ScreenRunPage>(`/api/screens/${encodeURIComponent(slug)}/refresh`, tokens, { method: "POST" }),
  rename: (id: number, name: string, tokens: AccessTokenProvider = browserAccessToken) =>
    request<{ id: number; name: string }>(`/api/screens/${id}`, tokens, { method: "PATCH", body: JSON.stringify({ name }) }),
  remove: (id: number, tokens: AccessTokenProvider = browserAccessToken) =>
    request<{ deleted: number }>(`/api/screens/${id}`, tokens, { method: "DELETE" }),
};

export const SAVED_QUERY_KEY = "scrooner.saved-screen-query";
