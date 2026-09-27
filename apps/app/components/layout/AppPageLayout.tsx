import type { ReactNode } from "react";

// Shared content frame for standard-width authenticated pages. Navigation
// stays in the global header, so product pages do not grow a second,
// competing sidebar navigation.
export function AppPageLayout({ children }: { children: ReactNode }) {
  return <div className="app-page-layout">{children}</div>;
}
