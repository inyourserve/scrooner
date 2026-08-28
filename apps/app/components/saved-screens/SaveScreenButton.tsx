"use client";

import { useState, type FormEvent } from "react";
import { Button } from "@/components/ui/Button";
import { savedScreensApi } from "@/lib/saved-screens/client";
import type { ScreenQueryPayload } from "@/lib/screener/types";

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
    {open && <form className="save-screen-form" onSubmit={save}>
      <label htmlFor="saved-screen-name">Screen name</label>
      <div><input id="saved-screen-name" autoFocus maxLength={120} value={name} onChange={(event) => setName(event.target.value)} aria-invalid={state === "error"} aria-describedby={message ? "save-screen-message" : undefined} />
      <Button type="submit" disabled={state === "saving"}>{state === "saving" ? "Saving…" : "Save"}</Button>
      <button type="button" className="text-button" onClick={() => setOpen(false)}>Cancel</button></div>
    </form>}
    {message && <p id="save-screen-message" className={state === "error" ? "field-error" : "save-screen-message"} role={state === "error" ? "alert" : "status"}>{message}</p>}
  </div>;
}

