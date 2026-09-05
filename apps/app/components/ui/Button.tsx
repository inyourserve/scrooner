import type { ButtonHTMLAttributes, ReactNode } from "react";

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "secondary" | "ghost" | "destructive";
  size?: "small" | "medium" | "large";
  fullWidth?: boolean;
  loading?: boolean;
  loadingLabel?: string;
  leadingIcon?: ReactNode;
  trailingIcon?: ReactNode;
};

export function Button({
  variant = "primary",
  size = "medium",
  fullWidth = false,
  loading = false,
  loadingLabel = "Working…",
  leadingIcon,
  trailingIcon,
  className = "",
  children,
  disabled,
  ...props
}: ButtonProps) {
  const classes = [
    "ds-button",
    `ds-button--${variant}`,
    size === "medium" ? "" : `ds-button--${size}`,
    fullWidth ? "ds-button--full" : "",
    className,
  ].filter(Boolean).join(" ");

  return (
    <button className={classes} disabled={disabled || loading} aria-busy={loading || undefined} {...props}>
      {loading ? <span className="ds-spinner ds-spinner--button" aria-hidden="true" /> : leadingIcon}
      <span>{loading ? loadingLabel : children}</span>
      {!loading && trailingIcon}
    </button>
  );
}
