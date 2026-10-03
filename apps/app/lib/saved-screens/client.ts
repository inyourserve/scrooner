import type { AccessTokenProvider, SavedScreen, ScreenRunPage } from "./types";
import type { ScreenQueryPayload } from "@/lib/screener/types";
import { createClient } from "@/lib/supabase/client";

const RUN_PAGE_NAVIGATION_KEY = "scrooner.run-page";
const pendingRuns = new Map<string, Promise<ScreenRunPage | Record<string, unknown>>>();

export function registerPendingRun(runId: string, request: Promise<ScreenRunPage | Record<string, unknown>>) {
  pendingRuns.set(runId, request);
  const cleanUp = () => window.setTimeout(() => pendingRuns.delete(runId), 30_000);
  void request.then(cleanUp, cleanUp);
}

export function readPendingRun(runId: string) {
  return pendingRuns.get(runId) ?? null;
}

export function cacheRunPageForNavigation(page: ScreenRunPage, pageSize: number) {
  if (typeof window === "undefined") return;
  try {
    window.sessionStorage.setItem(`${RUN_PAGE_NAVIGATION_KEY}:${page.run_id}:${pageSize}:first`, JSON.stringify(page));
  } catch {
    // Storage is only a navigation-speed optimization. The persisted run
    // remains the source of truth when storage is unavailable or full.
  }
}

export function readNavigationRunPage(runId: string, pageSize: number): ScreenRunPage | null {
  if (typeof window === "undefined") return null;
  try {
    const key = `${RUN_PAGE_NAVIGATION_KEY}:${runId}:${pageSize}:first`;
    const raw = window.sessionStorage.getItem(key);
    if (!raw) return null;
    return JSON.parse(raw) as ScreenRunPage;
  } catch {
    return null;
  }
}

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
  const response = await fetch(path, {
    ...init,
    headers: {
      accept: "application/json",
      ...(token ? { authorization: `Bearer ${token}` } : {}),
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
  createRun: (text: string, pageSize = 50, runId?: string) =>
    sessionRequest<ScreenRunPage | Record<string, unknown>>("/api/screen-runs", { method: "POST", body: JSON.stringify({ text, page_size: pageSize, run_id: runId }) }),
  createRunFromQuery: (text: string, query: ScreenQueryPayload, pageSize = 50) =>
    sessionRequest<ScreenRunPage>("/api/screen-runs", { method: "POST", body: JSON.stringify({ text, query, page_size: pageSize }) }),
  getRun: (id: string, cursor?: string, pageSize = 50) => {
    const params = new URLSearchParams({ page_size: String(pageSize) });
    if (cursor) params.set("cursor", cursor);
    return sessionRequest<ScreenRunPage>(`/api/screen-runs/${id}?${params}`);
  },
  refresh: (slug: string, tokens: AccessTokenProvider = browserAccessToken) =>
    request<ScreenRunPage>(`/api/screens/${encodeURIComponent(slug)}/refresh`, tokens, { method: "POST" }),
  rename: (id: number, name: string, tokens: AccessTokenProvider = browserAccessToken) =>
    request<{ id: number; name: string }>(`/api/screens/${id}`, tokens, { method: "PATCH", body: JSON.stringify({ name }) }),
  remove: (id: number, tokens: AccessTokenProvider = browserAccessToken) =>
    request<{ deleted: number }>(`/api/screens/${id}`, tokens, { method: "DELETE" }),
};

export const SAVED_QUERY_KEY = "scrooner.saved-screen-query";
