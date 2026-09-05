"use client";

import { useEffect, useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/Button";
import { StatusPanel } from "@/components/ui/StatusPanel";
import { Dialog } from "@/components/ui/Dialog";
import { Field } from "@/components/ui/Field";
import { SAVED_QUERY_KEY, savedScreensApi } from "@/lib/saved-screens/client";
import type { SavedScreen } from "@/lib/saved-screens/types";

function summary(screen: SavedScreen) {
  const metrics = screen.query.metric_predicates.length;
  const categories = screen.query.categorical_predicates.length;
  const count = metrics + categories;
  return `${count} ${count === 1 ? "criterion" : "criteria"}${screen.query.sort_by ? ` · sorted by ${screen.query.sort_by}` : ""}`;
}

export function SavedScreensClient() {
  const router = useRouter();
  const [screens, setScreens] = useState<SavedScreen[]>([]);
  const [state, setState] = useState<"loading" | "ready" | "error">("loading");
  const [message, setMessage] = useState("");
  const [renaming, setRenaming] = useState<SavedScreen | null>(null);
  const [name, setName] = useState("");
  const [deleting, setDeleting] = useState<SavedScreen | null>(null);

  async function load() {
    setState("loading"); setMessage("");
    try { setScreens(await savedScreensApi.list()); setState("ready"); }
    catch (error) { setState("error"); setMessage(error instanceof Error ? error.message : "Saved screens could not be loaded."); }
  }
  useEffect(() => {
    let active = true;
    void savedScreensApi.list().then((items) => {
      if (!active) return;
      setScreens(items); setState("ready");
    }).catch((error: unknown) => {
      if (!active) return;
      setState("error"); setMessage(error instanceof Error ? error.message : "Saved screens could not be loaded.");
    });
    return () => { active = false; };
  }, []);

  function run(screen: SavedScreen) {
    window.sessionStorage.setItem(SAVED_QUERY_KEY, JSON.stringify(screen.query));
    router.push("/screener?saved=1");
  }

  async function rename(event: FormEvent) {
    event.preventDefault();
    if (!renaming || !name.trim()) return;
    try {
      await savedScreensApi.rename(renaming.id, name.trim());
      setScreens((current) => current.map((item) => item.id === renaming.id ? { ...item, name: name.trim(), updated_at: new Date().toISOString() } : item));
      setRenaming(null); setMessage("Screen renamed.");
    } catch (error) { setMessage(error instanceof Error ? error.message : "The screen could not be renamed."); }
  }

  async function remove() {
    if (!deleting) return;
    try {
      await savedScreensApi.remove(deleting.id);
      setScreens((current) => current.filter((item) => item.id !== deleting.id));
      setDeleting(null); setMessage("Screen deleted.");
    } catch (error) { setMessage(error instanceof Error ? error.message : "The screen could not be deleted."); }
  }

  if (state === "loading") return <StatusPanel title="Loading saved screens" busy><p>Retrieving your reusable criteria.</p></StatusPanel>;
  if (state === "error") return <StatusPanel tone="negative" title="Saved screens are unavailable" action={<Button size="small" variant="ghost" onClick={() => void load()}>Try again</Button>}><p>{message}</p></StatusPanel>;
  return <>
    {message && <p className="saved-screen-status" role="status">{message}</p>}
    {screens.length === 0 ? <StatusPanel title="No saved screens yet"><p>Run a screen, then use Save screen to keep its criteria here.</p><a href="/screener">Build a screen</a></StatusPanel> :
      <div className="saved-screen-table-wrap"><table className="saved-screen-table"><caption className="sr-only">Your saved screens</caption><thead><tr><th scope="col">Screen</th><th scope="col">Criteria</th><th scope="col">Updated</th><th scope="col"><span className="sr-only">Actions</span></th></tr></thead><tbody>
      {screens.map((screen) => <tr key={screen.id}><th scope="row">{screen.name}</th><td>{summary(screen)}</td><td><time dateTime={screen.updated_at}>{new Date(screen.updated_at).toLocaleDateString()}</time></td><td className="saved-screen-actions"><Button size="small" onClick={() => run(screen)}>Run</Button><Button size="small" variant="ghost" onClick={() => { setRenaming(screen); setName(screen.name); }}>Rename</Button><Button size="small" variant="ghost" className="destructive" onClick={() => setDeleting(screen)}>Delete</Button></td></tr>)}
      </tbody></table></div>}
    {renaming && <Dialog title="Rename screen" onClose={() => setRenaming(null)}><form onSubmit={rename}><Field htmlFor="rename-screen" label="Screen name"><input className="ds-control" id="rename-screen" data-dialog-initial-focus maxLength={120} value={name} onChange={(event) => setName(event.target.value)} /></Field><div className="ds-dialog__actions"><Button type="button" variant="ghost" onClick={() => setRenaming(null)}>Cancel</Button><Button type="submit" disabled={!name.trim()}>Rename</Button></div></form></Dialog>}
    {deleting && <Dialog role="alertdialog" title={`Delete “${deleting.name}”?`} description="This removes the saved criteria. It cannot be undone." onClose={() => setDeleting(null)} actions={<><Button type="button" variant="ghost" onClick={() => setDeleting(null)}>Cancel</Button><Button type="button" variant="destructive" onClick={() => void remove()}>Delete screen</Button></>} />}
  </>;
}
