import type { ReactNode } from "react";

type FieldProps = {
  htmlFor: string;
  label: string;
  hint?: string;
  error?: string;
  errorId?: string;
  className?: string;
  children: ReactNode;
};

export function Field({ htmlFor, label, hint, error, errorId, className = "", children }: FieldProps) {
  return (
    <div className={["ds-field", className].filter(Boolean).join(" ")}>
      <label className="ds-label" htmlFor={htmlFor}>{label}</label>
      {children}
      {hint && !error && <p className="ds-help">{hint}</p>}
      {error && <p className="ds-error" id={errorId} role="alert">{error}</p>}
    </div>
  );
}
