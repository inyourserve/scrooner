import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Scrooner — Fundamental stock screening",
  description: "Build deterministic US fundamental screens and verify every result.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
