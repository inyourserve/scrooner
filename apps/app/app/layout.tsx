import type { Metadata } from "next";
import { AppShell } from "@/components/layout/AppShell";
import "./globals.css";
import "@/components/layout/app-shell.css";

export const metadata: Metadata = {
  title: "Scrooner — Fundamental stock screening",
  description: "Build deterministic US fundamental screens and verify every result.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        {/* Root App Router layout: this stylesheet is shared by every route. */}
        {/* eslint-disable-next-line @next/next/no-page-custom-font */}
        <link
          href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=Inter:wght@400;500;600&family=Newsreader:opsz,wght@6..72,400;6..72,500&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>
        <AppShell siteUrl={(process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:4321").replace(/\/$/, "")}>{children}</AppShell>
      </body>
    </html>
  );
}
