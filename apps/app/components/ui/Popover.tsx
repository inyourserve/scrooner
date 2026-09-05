"use client";

import { useEffect, useRef, type ReactNode } from "react";

export function Popover({ label, onClose, children, className = "" }: {
  label: string;
  onClose: () => void;
  children: ReactNode;
  className?: string;
}) {
  const panelRef = useRef<HTMLDivElement>(null);
  const onCloseRef = useRef(onClose);
  onCloseRef.current = onClose;

  useEffect(() => {
    const previousFocus = document.activeElement instanceof HTMLElement ? document.activeElement : null;
    const panel = panelRef.current;
    panel?.querySelector<HTMLElement>("[data-popover-initial-focus], input, button, [href]")?.focus({ preventScroll: true });

    function onKeyDown(event: globalThis.KeyboardEvent) {
      if (event.key === "Escape") {
        event.preventDefault();
        onCloseRef.current();
      }
    }
    function onPointerDown(event: PointerEvent) {
      if (panel && !panel.contains(event.target as Node)) onCloseRef.current();
    }
    document.addEventListener("keydown", onKeyDown);
    document.addEventListener("pointerdown", onPointerDown);
    return () => {
      document.removeEventListener("keydown", onKeyDown);
      document.removeEventListener("pointerdown", onPointerDown);
      previousFocus?.focus({ preventScroll: true });
    };
  }, []);

  return <div ref={panelRef} className={["ds-popover", className].filter(Boolean).join(" ")} role="dialog" aria-label={label}>{children}</div>;
}
