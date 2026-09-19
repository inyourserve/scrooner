import type { ReactNode } from "react";
import { PublicHeader } from "@/components/public/PublicHeader";

export function AppShell({ children, userEmail }: { children: ReactNode; userEmail: string }) {
  return (
    <div className="app-shell">
      <PublicHeader current="dashboard" userEmail={userEmail} skipHref="#main-content" />
      <div className="app-shell__stage">
        <div className="app-shell__content">{children}</div>
      </div>
    </div>
  );
}
