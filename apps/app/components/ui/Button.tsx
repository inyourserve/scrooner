import type { ButtonHTMLAttributes } from "react";

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "secondary" | "ghost" | "destructive";
  size?: "small" | "medium" | "large";
  fullWidth?: boolean;
};

export function Button({
  variant = "primary",
  size = "medium",
  fullWidth = false,
  className = "",
  ...props
}: ButtonProps) {
  const classes = [
    "ds-button",
    `ds-button--${variant}`,
    size === "medium" ? "" : `ds-button--${size}`,
    fullWidth ? "ds-button--full" : "",
    className,
  ].filter(Boolean).join(" ");

  return <button className={classes} {...props} />;
}
