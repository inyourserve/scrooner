// Redis-backed cache for the company page's one consolidated query
// (getCompanyPageData, lib/company/db.ts). Added 2026-09-15, same day as
// the unstable_cache fix in app/stocks/[ticker]/page.tsx -- that fix works,
// but Next's built-in cache (no custom handler configured) is per server
// instance/process, not shared -- fine for a single dev server, but under
// any horizontally-scaled deployment (more than one Next server process)
// every instance would independently pay the real ~1.5-7s query cost on
// its own first hit for every ticker. Redis is already a real production
// dependency of this monorepo (apps/backend, ADR 0001) for exactly this
// class of problem; this mirrors that module's own fail-open contract
// (apps/backend/cache.py) -- a cache outage must never make the company
// page unavailable, only slower (falls straight through to Postgres).
//
// Deliberately a SEPARATE Redis client/module from apps/backend's, even
// though both may point at the same Redis instance in production: this is
// a different process (Next.js, not FastAPI) with its own connection
// lifecycle, and the two were never meant to share key space (backend
// keys are `screen:*`/`auth-user:*`; this module's keys are
// `company-page:*`).

import { createClient } from "redis";
import type { CompanyPageData } from "./db";

const REDIS_URL = process.env.REDIS_URL;
const TTL_SECONDS = 15 * 60; // matches the page's own staleness budget --
// Alpaca's price feed (doc 25) is itself ~15min delayed, so caching for
// longer never makes the page meaningfully staler than its own source data.

// Lazily connected, reused across requests within one server process --
// `redis`'s client auto-reconnects on its own after a transient drop, so
// this is safe to hold as a long-lived module-level singleton the same way
// lib/company/db.ts holds its Postgres pool.
let clientPromise: ReturnType<typeof createClient> | null = null;

function getClient() {
  if (!REDIS_URL) return null;
  if (!clientPromise) {
    clientPromise = createClient({ url: REDIS_URL });
    // A cache is best-effort by design -- an unhandled 'error' event would
    // otherwise crash the Node process on any Redis hiccup (connection
    // refused, network blip). Every call site below already catches
    // failures around individual operations; this just keeps the client
    // itself alive to retry.
    clientPromise.on("error", () => {});
  }
  return clientPromise;
}

function key(ticker: string): string {
  return `company-page:${ticker.toLowerCase()}`;
}

export async function getCachedCompanyPage(ticker: string): Promise<CompanyPageData | null | undefined> {
  const client = getClient();
  if (!client) return undefined; // no REDIS_URL configured -- not a miss, just absent
  try {
    if (!client.isOpen) await client.connect();
    const raw = await client.get(key(ticker));
    if (raw == null) return undefined;
    return JSON.parse(raw) as CompanyPageData | null;
  } catch {
    // Redis accelerates repeat visits; it must never make the page
    // unavailable. Treat any failure (connect, GET, malformed JSON) as a
    // miss and fall through to the real query.
    return undefined;
  }
}

export async function setCachedCompanyPage(ticker: string, data: CompanyPageData | null): Promise<void> {
  const client = getClient();
  if (!client) return;
  try {
    if (!client.isOpen) await client.connect();
    await client.set(key(ticker), JSON.stringify(data), { EX: TTL_SECONDS });
  } catch {
    // Best-effort write: the query result is still returned to the caller
    // either way.
  }
}
