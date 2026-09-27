import type { Metadata, Viewport } from "next";
import "./globals.css";
import "@/components/layout/app-shell.css";
import "./public-theme.css";
import "./home.css";
import "./public-content.css";
import "./company-research.css";
import "./pricing.css";

const SITE_URL = process.env.NEXT_PUBLIC_SCROONER_URL ?? "https://scrooner.com";
const SITE_NAME = "Scrooner";
const SITE_DESCRIPTION = "Build deterministic US fundamental screens and verify every result.";

// `metadataBase` resolves every relative URL used in this file and in any
// page's own `openGraph`/`twitter` metadata (e.g. a per-page `images: [...]`
// entry) into an absolute one -- without it, Next.js falls back to
// inferring from the request and warns at build time, and social-preview
// images can silently break. `openGraph`/`twitter` here are just the
// site-wide default a page inherits unless it sets its own.
//
// Deliberately a plain `title` string, not `{ default, template }` --
// every page in this app that sets its own title (e.g. /stocks/[ticker]'s
// generateMetadata) already builds the FULL string itself, including its
// own " — Scrooner" suffix. A title template would apply on top of that
// and double the suffix ("AAPL — Scrooner — Scrooner"); simpler and safer
// to keep title composition fully in each page's own hands.
export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: `${SITE_NAME} — Fundamental stock screening`,
  description: SITE_DESCRIPTION,
  openGraph: {
    type: "website",
    siteName: SITE_NAME,
    title: `${SITE_NAME} — Fundamental stock screening`,
    description: SITE_DESCRIPTION,
    url: SITE_URL,
  },
  twitter: {
    card: "summary",
    title: `${SITE_NAME} — Fundamental stock screening`,
    description: SITE_DESCRIPTION,
  },
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
