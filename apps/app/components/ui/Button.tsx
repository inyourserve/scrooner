import { Slot, Slottable } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";
import type { ButtonHTMLAttributes, ReactNode } from "react";
import { cn } from "@/lib/utils";

export const buttonVariants = cva("ds-button", {
  variants: {
    variant: {
      primary: "ds-button--primary",
      secondary: "ds-button--secondary",
      ghost: "ds-button--ghost",
      destructive: "ds-button--destructive",
    },
    size: {
      small: "ds-button--small",
      medium: "",
      large: "ds-button--large",
    },
    fullWidth: {
      true: "ds-button--full",
      false: "",
    },
  },
  defaultVariants: { variant: "primary", size: "medium", fullWidth: false },
});

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & VariantProps<typeof buttonVariants> & {
  loading?: boolean;
  loadingLabel?: string;
  leadingIcon?: ReactNode;
  trailingIcon?: ReactNode;
  asChild?: boolean;
};

export function Button({
  variant = "primary",
  size = "medium",
  fullWidth = false,
  loading = false,
  loadingLabel = "Working…",
  leadingIcon,
  trailingIcon,
  asChild = false,
  className = "",
  children,
  disabled,
  ...props
}: ButtonProps) {
  const classes = cn(buttonVariants({ variant, size, fullWidth }), className);
  const Component = asChild ? Slot : "button";

  return (
    <Component data-slot="button" className={classes} disabled={asChild ? undefined : disabled || loading} aria-busy={loading || undefined} {...props}>
      {loading ? <span className="ds-spinner ds-spinner--button" aria-hidden="true" /> : leadingIcon}
      <Slottable>{asChild ? children : <span>{loading ? loadingLabel : children}</span>}</Slottable>
      {!loading && trailingIcon}
    </Component>
  );
}
