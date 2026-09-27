"use client";

import { useEffect, useState, type FormEvent } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { AppPageLayout } from "@/components/layout/AppPageLayout";
import { Button } from "@/components/ui/Button";
import { Card, CardContent, CardDescription, CardHeader, CardHeading, CardTitle } from "@/components/ui/Card";
import { Field } from "@/components/ui/Field";
import { StatusPanel } from "@/components/ui/StatusPanel";
import { savedScreensApi } from "@/lib/saved-screens/client";
import type { ScreenQueryPayload } from "@/lib/screener/types";
import { SAVE_QUERY_SESSION_KEY } from "./SaveScreenButton";

type State = "loading" | "ready" | "saving" | "error";

export function SaveScreenPageClient() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const runId = searchParams.get("run") || undefined;
  const queryText = searchParams.get("query") || "";
  const returnTo = searchParams.get("from");
  const [query, setQuery] = useState<ScreenQueryPayload | null>(null);
  const [name, setName] = useState("");
  const [state, setState] = useState<State>("loading");
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    const key = runId || "draft";
    const stored = window.sessionStorage.getItem(`${SAVE_QUERY_SESSION_KEY}:${key}`);
    if (stored) {
      try {
        const parsed = JSON.parse(stored) as ScreenQueryPayload;
        window.queueMicrotask(() => {
          if (!active) return;
          setQuery(parsed);
          setState("ready");
        });
        return () => { active = false; };
      } catch {
        window.sessionStorage.removeItem(`${SAVE_QUERY_SESSION_KEY}:${key}`);
      }
    }
    if (!runId) {
      window.queueMicrotask(() => {
        if (!active) return;
        setState("error");
        setError("The screen criteria are unavailable. Return to the results and choose Save screen again.");
      });
      return () => { active = false; };
    }
    const size = Number(searchParams.get("limit")) || 10;
    void savedScreensApi.getRun(runId, undefined, size).then((run) => {
      if (!active) return;
      setQuery(run.normalized_query);
      setState("ready");
    }).catch((loadError: unknown) => {
      if (!active) return;
      setState("error");
      setError(loadError instanceof Error ? loadError.message : "The screen could not be loaded.");
    });
    return () => { active = false; };
  }, [runId, searchParams]);

  async function save(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const clean = name.trim();
    if (!clean) {
      setError("Enter a name for this screen.");
      return;
    }
    if (!query) return;
    setState("saving");
    setError("");
    try {
      const saved = await savedScreensApi.create(clean, query, runId);
      window.sessionStorage.removeItem(`${SAVE_QUERY_SESSION_KEY}:${runId || "draft"}`);
      router.push(`/app/screens/${saved.slug}`);
    } catch (saveError) {
      setState("ready");
      setError(saveError instanceof Error ? saveError.message : "The screen could not be saved.");
    }
  }

  function goBack() {
    if (returnTo?.startsWith("/app/screens/new")) {
      router.push(returnTo);
      return;
    }
    router.back();
  }

  return (
    <main className="main-content" id="main-content">
      <AppPageLayout>
        <Card className="save-query-card" aria-labelledby="save-query-title">
          <CardHeader><CardHeading><CardTitle id="save-query-title">Save screen</CardTitle><CardDescription>Name this screen so you can run it again later.</CardDescription></CardHeading></CardHeader>
          <CardContent>
          {state === "loading" && <StatusPanel title="Loading query" busy><p>Preparing the saved screen.</p></StatusPanel>}
          {state === "error" && !query && <StatusPanel tone="negative" title="Query unavailable"><p>{error}</p></StatusPanel>}
          {query && <form onSubmit={save}>
            <Field htmlFor="saved-screen-name" label="Name" error={error || undefined} errorId="save-screen-error">
              <input className="ds-control" id="saved-screen-name" maxLength={120} autoFocus value={name} onChange={(event) => { setName(event.target.value); setError(""); }} placeholder="e.g. Durable compounders" aria-invalid={Boolean(error)} aria-describedby={error ? "save-screen-error" : undefined} />
            </Field>
            <div className="save-query-preview"><strong>Query</strong><p>{queryText || "Structured fundamental screen"}</p></div>
            <p className="save-query-privacy">Saved screens are private to your account.</p>
            <div className="save-query-actions">
              <Button type="button" variant="ghost" onClick={goBack}>← Go back</Button>
              <Button type="submit" loading={state === "saving"} loadingLabel="Saving…">Save screen</Button>
            </div>
          </form>}
          </CardContent>
        </Card>
      </AppPageLayout>
    </main>
  );
}
