import { forwardRef, type InputHTMLAttributes, type TextareaHTMLAttributes } from "react";
import { cn } from "@/lib/utils";

type ControlStyleProps = {
  size?: "medium" | "large";
  numeric?: boolean;
};

export type InputProps = Omit<InputHTMLAttributes<HTMLInputElement>, "size"> & ControlStyleProps;

export const Input = forwardRef<HTMLInputElement, InputProps>(function Input(
  { size = "medium", numeric = false, className, ...props },
  ref,
) {
  return (
    <input
      ref={ref}
      data-slot="input"
      className={cn(
        "ds-control",
        size === "large" && "ds-control--large",
        numeric && "ds-control--mono",
        className,
      )}
      {...props}
    />
  );
});

export type TextareaProps = TextareaHTMLAttributes<HTMLTextAreaElement> & ControlStyleProps;

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(function Textarea(
  { size = "medium", numeric = false, className, ...props },
  ref,
) {
  return (
    <textarea
      ref={ref}
      data-slot="textarea"
      className={cn(
        "ds-control",
        size === "large" && "ds-control--large",
        numeric && "ds-control--mono",
        className,
      )}
      {...props}
    />
  );
});
