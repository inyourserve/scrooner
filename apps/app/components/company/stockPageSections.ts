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
  { id: "chart", label: "Price chart" }, { id: "quarterly-results", label: "Quarterly results" },
  { id: "profit-loss", label: "Income statement" }, { id: "balance-sheet", label: "Balance sheet" },
  { id: "cash-flow", label: "Cash flow" }, { id: "ratios", label: "Financial ratios" },
  { id: "peers", label: "Peer comparison" }, { id: "shareholding", label: "Ownership" },
  { id: "documents", label: "SEC filings" },
];
