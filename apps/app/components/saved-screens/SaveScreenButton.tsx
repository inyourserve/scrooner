"use client";

import { useState, type FormEvent } from "react";
import { Button } from "@/components/ui/Button";
import { savedScreensApi } from "@/lib/saved-screens/client";
import type { ScreenQueryPayload } from "@/lib/screener/types";
import { Field } from "@/components/ui/Field";
import { Popover } from "@/components/ui/Popover";

export function SaveScreenButton({ query }: { query: ScreenQueryPayload }) {
  const [open, setOpen] = useState(false);
  const [name, setName] = useState("");
  const [state, setState] = useState<"idle" | "saving" | "saved" | "error">("idle");
  const [message, setMessage] = useState("");

  async function save(event: FormEvent) {
    event.preventDefault();
    const clean = name.trim();
    if (!clean) { setState("error"); setMessage("Enter a name for this screen."); return; }
    setState("saving");
    try {
      await savedScreensApi.create(clean, query);
      setState("saved"); setMessage(`“${clean}” was saved.`); setName(""); setOpen(false);
    } catch (error) {
      setState("error"); setMessage(error instanceof Error ? error.message : "The screen could not be saved.");
    }
  }

  return <div className="save-screen-control">
    <Button type="button" variant="secondary" onClick={() => { setOpen(true); setState("idle"); setMessage(""); }}>Save screen</Button>
    {open && <Popover label="Save screen" onClose={() => setOpen(false)} className="save-screen-form"><form onSubmit={save}>
      <Field htmlFor="saved-screen-name" label="Screen name" error={state === "error" ? message : undefined} errorId="save-screen-message">
        <input className="ds-control" id="saved-screen-name" data-popover-initial-focus maxLength={120} value={name} onChange={(event) => setName(event.target.value)} aria-invalid={state === "error"} aria-describedby={message ? "save-screen-message" : undefined} />
      </Field>
      <div className="save-screen-form__actions"><Button type="button" variant="ghost" onClick={() => setOpen(false)}>Cancel</Button><Button type="submit" loading={state === "saving"} loadingLabel="Saving…">Save</Button></div>
    </form></Popover>}
    {message && state !== "error" && <p id="save-screen-message" className="save-screen-message" role="status">{message}</p>}
  </div>;
}
