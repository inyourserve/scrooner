import type { Metadata, Viewport } from "next";
import "./globals.css";
import "@/components/layout/app-shell.css";
import "./public-theme.css";
import "./home.css";
import "./public-content.css";
import "./company-research.css";
import "./pricing.css";

export const metadata: Metadata = {
  title: "Scrooner — Fundamental stock screening",
  description: "Build deterministic US fundamental screens and verify every result.",
};

// Missing entirely until now -- every mobile browser was rendering this
// site at a desktop-width virtual viewport (~980px) and shrinking it to
// fit, since nothing told it the page is actually responsive. That's
// exactly what "everything is misaligned" looks like on a real phone.
export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
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
      <body>{children}</body>
    </html>
  );
}
