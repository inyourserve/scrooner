"use client";

import Link from "next/link";
import { useState, type FormEvent } from "react";
import { ArrowRight, Pencil, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { StatusPanel } from "@/components/ui/StatusPanel";
import { Dialog } from "@/components/ui/Dialog";
import { Field } from "@/components/ui/Field";
import { EmptyState } from "@/components/scrooner/EmptyState";
import { savedScreensApi } from "@/lib/saved-screens/client";
import type { SavedScreen } from "@/lib/saved-screens/types";
import styles from "./saved-screens.module.css";

function criterionCount(screen: SavedScreen) {
  return screen.query.metric_predicates.length + screen.query.categorical_predicates.length;
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat(undefined, { day: "numeric", month: "short", year: "numeric" }).format(new Date(value));
}

export function SavedScreensClient({ initialScreens }: { initialScreens: SavedScreen[] }) {
  const [screens, setScreens] = useState<SavedScreen[]>(initialScreens);
  const [state, setState] = useState<"loading" | "ready" | "error">("ready");
  const [message, setMessage] = useState("");
  const [renaming, setRenaming] = useState<SavedScreen | null>(null);
  const [name, setName] = useState("");
  const [deleting, setDeleting] = useState<SavedScreen | null>(null);
  const [pendingAction, setPendingAction] = useState<"rename" | "delete" | null>(null);

  async function load() {
    setState("loading");
    setMessage("");
    try {
      setScreens(await savedScreensApi.list());
      setState("ready");
    } catch (error) {
      setState("error");
      setMessage(error instanceof Error ? error.message : "Saved screens could not be loaded.");
    }
  }

  async function rename(event: FormEvent) {
    event.preventDefault();
    const cleanName = name.trim();
    if (!renaming || !cleanName) return;
    setPendingAction("rename");
    try {
      await savedScreensApi.rename(renaming.id, cleanName);
      setScreens((current) => current.map((item) => item.id === renaming.id ? { ...item, name: cleanName, updated_at: new Date().toISOString() } : item));
      setRenaming(null);
      setMessage("Screen renamed.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "The screen could not be renamed.");
    } finally {
      setPendingAction(null);
    }
  }

  async function remove() {
    if (!deleting) return;
    setPendingAction("delete");
    try {
      await savedScreensApi.remove(deleting.id);
      setScreens((current) => current.filter((item) => item.id !== deleting.id));
      setDeleting(null);
      setMessage("Screen deleted.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "The screen could not be deleted.");
    } finally {
      setPendingAction(null);
    }
  }

  if (state === "loading") return <StatusPanel title="Loading saved screens" busy><p>Retrieving your screen library.</p></StatusPanel>;
  if (state === "error") return <StatusPanel tone="negative" title="Saved screens are unavailable" action={<Button size="small" variant="ghost" onClick={() => void load()}>Try again</Button>}><p>{message}</p></StatusPanel>;

  return (
    <>
      {message && <p className={styles.status} role="status">{message}</p>}
      {screens.length === 0 ? (
        <EmptyState title="No saved screens yet" description="Build a screen and save its criteria to create your research library." action={<Button asChild size="small" variant="secondary"><Link href="/app/screens/new">Build a screen</Link></Button>} />
      ) : (
        <section className={styles.library} aria-labelledby="screen-library-title">
          <header className={styles.libraryHeader}>
            <div><h2 id="screen-library-title">Your library</h2><p>{screens.length} saved {screens.length === 1 ? "screen" : "screens"}</p></div>
            <span className={styles.freshness}>Saved results</span>
          </header>
          <ul className={styles.list}>
            {screens.map((screen) => {
              const count = criterionCount(screen);
              return (
                <li className={styles.item} key={screen.id}>
                  <Link className={styles.primaryAction} href={`/app/screens/${screen.slug}`} aria-label={`Open ${screen.name}`}>
                    <span className={styles.screenIdentity}>
                      <strong>{screen.name}</strong>
                      <span>{count} {count === 1 ? "criterion" : "criteria"}{screen.query.sort_by ? <> · Sort: <code>{screen.query.sort_by}</code></> : null}</span>
                    </span>
                    <span className={styles.runLabel}>Open <ArrowRight size={14} aria-hidden="true" /></span>
                  </Link>
                  <time className={styles.updated} dateTime={screen.updated_at}>Updated {formatDate(screen.updated_at)}</time>
                  <div className={styles.actions}>
                    <Button size="small" variant="ghost" leadingIcon={<Pencil size={14} aria-hidden="true" />} onClick={() => { setRenaming(screen); setName(screen.name); }}>Rename</Button>
                    <Button size="small" variant="ghost" className={styles.deleteButton} leadingIcon={<Trash2 size={14} aria-hidden="true" />} onClick={() => setDeleting(screen)}>Delete</Button>
                  </div>
                </li>
              );
            })}
          </ul>
        </section>
      )}

      {renaming && <Dialog title="Rename screen" onClose={() => setRenaming(null)}><form onSubmit={rename}><Field htmlFor="rename-screen" label="Screen name"><input className="ds-control" id="rename-screen" data-dialog-initial-focus maxLength={120} value={name} onChange={(event) => setName(event.target.value)} /></Field><div className="ds-dialog__actions"><Button type="button" variant="ghost" onClick={() => setRenaming(null)}>Cancel</Button><Button type="submit" disabled={!name.trim()} loading={pendingAction === "rename"} loadingLabel="Renaming…">Rename</Button></div></form></Dialog>}
      {deleting && <Dialog role="alertdialog" title={`Delete “${deleting.name}”?`} description="This removes the saved criteria. It cannot be undone." onClose={() => setDeleting(null)} actions={<><Button type="button" variant="ghost" onClick={() => setDeleting(null)}>Cancel</Button><Button type="button" variant="destructive" loading={pendingAction === "delete"} loadingLabel="Deleting…" onClick={() => void remove()}>Delete screen</Button></>} />}
    </>
  );
}
