import type { HTMLAttributes, ReactNode } from "react";
import { cn } from "@/lib/utils";

type PageShellProps = HTMLAttributes<HTMLElement> & {
  children: ReactNode;
};

export function PageShell({ className, children, id = "main-content", ...props }: PageShellProps) {
  return <main id={id} className={cn("ds-page", className)} {...props}>{children}</main>;
}
