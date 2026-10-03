"use client";

import { Moon, Sun } from "lucide-react";

export function ThemeToggle() {
  return <button className="theme-toggle" type="button" aria-label="Toggle color theme" title="Toggle color theme" onClick={() => {
    const explicit = document.documentElement.dataset.theme;
    const dark = explicit === "dark" || (explicit !== "light" && window.matchMedia("(prefers-color-scheme: dark)").matches);
    const next = dark ? "light" : "dark";
    document.documentElement.dataset.theme = next;
    window.localStorage.setItem("scrooner-theme", next);
  }}>
    <Moon className="theme-toggle__moon" size={17} aria-hidden="true" />
    <Sun className="theme-toggle__sun" size={17} aria-hidden="true" />
  </button>;
}
