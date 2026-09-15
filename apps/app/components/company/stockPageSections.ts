import type { StockSectionLink } from "./StockSectionNav";

// Shared between app/stocks/[ticker]/page.tsx and its loading.tsx --
// Next.js's typed routes validate that a page.tsx file only exports its own
// known special names (default, metadata, dynamic, etc.), so this couldn't
// live as a named export on the page module itself (found live 2026-09-15,
// a real `tsc` error: "Property 'sections' is incompatible with index
// signature"). A static list, not derived from fetched data, so both files
// can render the identical nav instantly.
export const stockPageSections: StockSectionLink[] = [
  { id: "overview", label: "Overview" }, { id: "analysis", label: "Analysis" },
  { id: "chart", label: "Chart" }, { id: "quarterly-results", label: "Quarters" },
  { id: "profit-loss", label: "Income" }, { id: "balance-sheet", label: "Balance sheet" },
  { id: "cash-flow", label: "Cash flow" }, { id: "ratios", label: "Ratios" },
  { id: "peers", label: "Peers" }, { id: "shareholding", label: "Ownership" },
  { id: "documents", label: "Documents" },
];
