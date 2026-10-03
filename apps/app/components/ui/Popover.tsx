"use client";

import { useEffect, useRef, type ReactNode } from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const popoverVariants = cva("ds-popover", {
  variants: {
    size: {
      small: "ds-popover--small",
      medium: "",
      large: "ds-popover--large",
    },
    align: {
      start: "ds-popover--start",
      end: "",
    },
    padded: {
      true: "",
      false: "ds-popover--flush",
    },
  },
  defaultVariants: { size: "medium", align: "end", padded: true },
});

type PopoverProps = {
  label: string;
  onClose: () => void;
  children: ReactNode;
  className?: string;
} & VariantProps<typeof popoverVariants>;

export function Popover({ label, onClose, children, className, size, align, padded }: PopoverProps) {
  const panelRef = useRef<HTMLDivElement>(null);
  const onCloseRef = useRef(onClose);
  useEffect(() => { onCloseRef.current = onClose; }, [onClose]);

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

  return <div ref={panelRef} data-slot="popover" className={cn(popoverVariants({ size, align, padded }), className)} role="dialog" aria-label={label}>{children}</div>;
}
