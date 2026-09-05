import type { ButtonHTMLAttributes, ReactNode } from "react";

type IconButtonProps = Omit<ButtonHTMLAttributes<HTMLButtonElement>, "children"> & {
  label: string;
  icon: ReactNode;
  tone?: "neutral" | "destructive";
  size?: "small" | "medium";
};

export function IconButton({ label, icon, tone = "neutral", size = "medium", className = "", ...props }: IconButtonProps) {
  const classes = [
    "ds-icon-button",
    tone === "destructive" ? "ds-icon-button--destructive" : "",
    size === "small" ? "ds-icon-button--small" : "",
    className,
  ].filter(Boolean).join(" ");

  return <button type="button" className={classes} aria-label={label} title={label} {...props}>{icon}</button>;
}
