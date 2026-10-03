"use client";

import { useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import { savedScreensApi } from "@/lib/saved-screens/client";
import type { ScreenQueryPayload } from "@/lib/screener/types";
import { Button } from "@/components/ui/Button";
import { Dialog } from "@/components/ui/Dialog";
import { Field } from "@/components/ui/Field";
import { Input } from "@/components/ui/Input";
import { StatusPanel } from "@/components/ui/StatusPanel";

export const SAVE_QUERY_SESSION_KEY = "scrooner.save-query";

type SaveState = "idle" | "saving" | "saved";
type SavedScreen = { id: number; name: string; slug: string };

export function SaveScreenButton({ query, runId }: { query: ScreenQueryPayload; runId?: string }) {
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [name, setName] = useState("");
  const [nameError, setNameError] = useState("");
  const [error, setError] = useState("");
  const [state, setState] = useState<SaveState>("idle");
  const [saved, setSaved] = useState<SavedScreen | null>(null);

  function close() {
    setOpen(false);
    setNameError("");
    setError("");
    if (state === "saved") {
      setName("");
      setSaved(null);
      setState("idle");
    }
  }

  async function save(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const clean = name.trim();
    if (!clean) {
      setNameError("Enter a name for this screen.");
      return;
    }

    setState("saving");
    setError("");
    try {
      const created = await savedScreensApi.create(clean, query, runId);
      setSaved(created);
      setState("saved");
    } catch (saveError) {
      setState("idle");
      setError(saveError instanceof Error ? saveError.message : "The screen could not be saved.");
    }
  }

  return (
    <div className="save-screen-control">
      <Button type="button" variant="primary" onClick={() => setOpen(true)}>Save screen</Button>
      {open && (
        <Dialog
          title={state === "saved" ? "Screen saved" : "Save screen"}
          description={state === "saved" ? undefined : "Name this screen so you can run it again later."}
          size="small"
          onClose={close}
        >
          {state === "saved" && saved ? (
            <>
              <StatusPanel tone="positive" title={`“${saved.name}” is in your library.`}>
                <p>Your current query results are still here.</p>
              </StatusPanel>
              <div className="ds-dialog__actions">
                <Button type="button" variant="ghost" onClick={close}>Stay on results</Button>
                <Button type="button" onClick={() => router.push(`/app/screens/${saved.slug}`)}>View saved screen</Button>
              </div>
            </>
          ) : (
            <form onSubmit={save}>
              {error && <StatusPanel tone="negative" title="Screen could not be saved"><p>{error}</p></StatusPanel>}
              <Field htmlFor="saved-screen-name" label="Screen name" error={nameError || undefined} errorId="save-screen-name-error">
                <Input
                  id="saved-screen-name"
                  data-dialog-initial-focus
                  maxLength={120}
                  value={name}
                  onChange={(event) => { setName(event.target.value); setNameError(""); }}
                  placeholder="e.g. Durable compounders"
                  aria-invalid={Boolean(nameError)}
                  aria-describedby={nameError ? "save-screen-name-error" : undefined}
                />
              </Field>
              <p className="ds-help">Saved screens are private to your account.</p>
              <div className="ds-dialog__actions">
                <Button type="button" variant="ghost" onClick={close}>Cancel</Button>
                <Button type="submit" loading={state === "saving"} loadingLabel="Saving…">Save screen</Button>
              </div>
            </form>
          )}
        </Dialog>
      )}
    </div>
  );
}
