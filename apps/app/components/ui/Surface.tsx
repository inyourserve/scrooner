import type { HTMLAttributes, ReactNode } from "react";

type SurfaceProps = HTMLAttributes<HTMLDivElement> & {
  raised?: boolean;
  padded?: boolean;
  children: ReactNode;
};

export function Surface({ raised = false, padded = false, className = "", children, ...props }: SurfaceProps) {
  return (
    <div
      className={["ds-surface", raised ? "ds-surface--raised" : "", padded ? "ds-surface--padded" : "", className].filter(Boolean).join(" ")}
      {...props}
    >
      {children}
    </div>
  );
}
