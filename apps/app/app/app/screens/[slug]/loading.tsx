import { TableSkeleton } from "@/components/scrooner/TableSkeleton";

// Same reasoning as ../loading.tsx: a per-user page's cached response
// still needs a first real fetch on every fresh visit. Column labels are a
// representative default (the real set depends on the saved query, not
// known before it loads) -- a shape to fill, not a claim about this
// specific screen's actual metrics.
export default function ScreenDetailLoading() {
  return (
    <main className="workspace-page saved-screen-detail" id="main-content" aria-busy="true" aria-label="Loading saved screen">
      <header className="saved-screen-detail__header">
        <div>
          <span className="ds-skeleton ds-skeleton--text" style={{ width: "10ch" }} />
          <h1><span className="ds-skeleton ds-skeleton--text" style={{ width: "16ch", height: "1.4em" }} /></h1>
        </div>
      </header>
      <TableSkeleton columnLabels={["ROE", "ROIC", "Market cap"]} />
    </main>
  );
}
