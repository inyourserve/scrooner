"use client";

import { useEffect, useId, useRef, type ReactNode } from "react";
import { IconButton } from "./IconButton";

type DialogProps = {
  title: string;
  description?: string;
  role?: "dialog" | "alertdialog";
  onClose: () => void;
  children?: ReactNode;
  actions?: ReactNode;
  closeLabel?: string;
};

const FOCUSABLE = [
  "button:not([disabled])",
  "[href]",
  "input:not([disabled])",
  "select:not([disabled])",
  "textarea:not([disabled])",
  "[tabindex]:not([tabindex='-1'])",
].join(",");

export function Dialog({
  title,
  description,
  role = "dialog",
  onClose,
  children,
  actions,
  closeLabel = "Close dialog",
}: DialogProps) {
  const generatedId = useId();
  const titleId = `${generatedId}-title`;
  const descriptionId = description ? `${generatedId}-description` : undefined;
  const panelRef = useRef<HTMLElement>(null);
  const onCloseRef = useRef(onClose);
  useEffect(() => { onCloseRef.current = onClose; }, [onClose]);

  useEffect(() => {
    const previousFocus = document.activeElement instanceof HTMLElement ? document.activeElement : null;
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";

    const panel = panelRef.current;
    const initial = panel?.querySelector<HTMLElement>("[data-dialog-initial-focus], [autofocus]")
      ?? panel?.querySelector<HTMLElement>("input, button, [href], select, textarea");
    initial?.focus({ preventScroll: true });

    function onKeyDown(event: globalThis.KeyboardEvent) {
      if (event.key === "Escape") {
        event.preventDefault();
        onCloseRef.current();
        return;
      }
      if (event.key !== "Tab" || !panel) return;
      const focusable = Array.from(panel.querySelectorAll<HTMLElement>(FOCUSABLE));
      if (focusable.length === 0) {
        event.preventDefault();
        panel.focus();
        return;
      }
      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    }

    document.addEventListener("keydown", onKeyDown);
    return () => {
      document.removeEventListener("keydown", onKeyDown);
      document.body.style.overflow = previousOverflow;
      previousFocus?.focus({ preventScroll: true });
    };
  }, []);

  return (
    <div className="ds-dialog-backdrop" onMouseDown={(event) => {
      if (event.target === event.currentTarget) onClose();
    }}>
      <section
        ref={panelRef}
        className="ds-dialog"
        role={role}
        aria-modal="true"
        aria-labelledby={titleId}
        aria-describedby={descriptionId}
        tabIndex={-1}
      >
        <div className="ds-dialog__header">
          <h2 id={titleId}>{title}</h2>
          <IconButton label={closeLabel} icon={<span aria-hidden="true">×</span>} onClick={onClose} />
        </div>
        {description && <p className="ds-dialog__description" id={descriptionId}>{description}</p>}
        {children && <div className="ds-dialog__body">{children}</div>}
        {actions && <div className="ds-dialog__actions">{actions}</div>}
      </section>
    </div>
  );
}
