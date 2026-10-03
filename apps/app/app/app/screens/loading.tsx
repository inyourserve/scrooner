import { Plus } from "lucide-react";
import { PageHeader } from "@/components/layout/PageHeader";
import { Button } from "@/components/ui/Button";
import Link from "next/link";
import listStyles from "@/components/saved-screens/saved-screens.module.css";
import styles from "../saved-screens/saved-screens.module.css";
import { PageShell } from "@/components/layout/PageShell";

// Even with routers/saved_screens.py's list_screens now Redis-cached
// (doc/learnings/2026-09-15-company-page-caching.md), a per-user page like
// this one can never be pre-warmed the way a public ticker page can (the
// cache key is per-viewer, there's no "popular screens list" to keep hot
// in advance) -- so a real, if now much shorter, wait is unavoidable on
// every fresh page load. Shaped after SavedScreensClient's own real markup
// (same CSS module classes) so the swap from this to the real list is
// instant with no layout jump, same principle as TableSkeleton and the
// stock page's own loading.tsx.
export default function ScreensLoading() {
  return (
    <PageShell className={styles.page}>
      <div className={styles.heading}>
        <PageHeader eyebrow="Screen library" title="Saved screens" description="Reopen your investment criteria, review saved results, or refresh them against the latest available data." />
        <Button asChild leadingIcon={<Plus size={16} aria-hidden="true" />}><Link href="/app/screens/new">Create screen</Link></Button>
      </div>
      <div className={styles.note}>
        <span aria-hidden="true" className={styles.noteMark}>i</span>
        <p><strong>Saved results open instantly.</strong> Refresh a screen only when you need the latest available data.</p>
      </div>
      <section className={listStyles.library} aria-busy="true" aria-label="Loading your saved screens">
        <header className={listStyles.libraryHeader}>
          <div><span className="ds-skeleton ds-skeleton--text" style={{ width: "10ch" }} /></div>
        </header>
        <ul className={listStyles.list}>
          {Array.from({ length: 3 }).map((_, index) => (
            <li className={listStyles.item} key={index} aria-hidden="true">
              <div className={listStyles.screenIdentity}>
                <span className="ds-skeleton ds-skeleton--text" style={{ width: "40%" }} />
                <span className="ds-skeleton ds-skeleton--text ds-skeleton--sub" style={{ width: "25%" }} />
              </div>
              <span className="ds-skeleton ds-skeleton--text" style={{ width: "8ch" }} />
              <span />
            </li>
          ))}
        </ul>
      </section>
    </PageShell>
  );
}
