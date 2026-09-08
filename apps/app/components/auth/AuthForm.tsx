"use client";

import Link from "next/link";
import { Eye, EyeOff } from "lucide-react";
import { useActionState, useState } from "react";
import {
  login,
  requestPasswordReset,
  signup,
  updatePassword,
} from "@/app/auth/actions";
import { INITIAL_AUTH_STATE, type AuthActionState } from "@/lib/auth/state";
import { Button } from "@/components/ui/Button";
import { Field } from "@/components/ui/Field";
import { IconButton } from "@/components/ui/IconButton";
import { StatusPanel } from "@/components/ui/StatusPanel";
import { OAuthButtons } from "./OAuthButtons";

type Mode = "login" | "signup" | "recovery" | "update";

const ACTIONS: Record<Mode, (state: AuthActionState, data: FormData) => Promise<AuthActionState>> = {
  login,
  signup,
  recovery: requestPasswordReset,
  update: updatePassword,
};

const COPY = {
  login: { title: "Welcome back", submit: "Sign in" },
  signup: { title: "Create your account", submit: "Create account" },
  recovery: { title: "Reset your password", submit: "Send reset link" },
  update: { title: "Choose a new password", submit: "Update password" },
} as const;

// Recovery and signup both end in "we emailed you something," not a
// redirect -- leaving the filled-in form sitting there invites a second,
// confusing submission. Swap the whole card for a plain confirmation
// instead of just printing a message above an still-active form.
const EMAIL_TAKEOVER_MODES = new Set<Mode>(["recovery", "signup"]);
// SSO only makes sense as an entry point, not for a password-specific flow.
const OAUTH_MODES = new Set<Mode>(["login", "signup"]);

function PasswordField({
  id,
  name,
  label,
  autoComplete,
  hint,
  error,
  errorId,
  autoFocus,
  invalid,
}: {
  id: string;
  name: string;
  label: string;
  autoComplete: string;
  hint?: string;
  error?: string;
  errorId: string;
  autoFocus?: boolean;
  /** Marks the field invalid without rendering its own error text -- for a
      "confirm password" field sharing one visible message with its
      sibling, the same way the two fields shared aria-describedby before
      this was extracted into its own component. */
  invalid?: boolean;
}) {
  const [visible, setVisible] = useState(false);
  const isInvalid = invalid ?? Boolean(error);
  return (
    <Field className="auth-field" htmlFor={id} label={label} hint={hint} error={error} errorId={errorId}>
      <div className="auth-password-field">
        <input
          className="ds-control"
          id={id}
          name={name}
          type={visible ? "text" : "password"}
          autoComplete={autoComplete}
          minLength={8}
          required
          autoFocus={autoFocus}
          aria-invalid={isInvalid}
          aria-describedby={isInvalid ? errorId : undefined}
        />
        <IconButton
          className="auth-password-field__toggle"
          size="small"
          label={visible ? "Hide password" : "Show password"}
          icon={visible ? <EyeOff size={16} aria-hidden="true" /> : <Eye size={16} aria-hidden="true" />}
          onClick={() => setVisible((value) => !value)}
        />
      </div>
    </Field>
  );
}

export function AuthForm({ mode, redirectUrl = "/app" }: { mode: Mode; redirectUrl?: string }) {
  const [state, action, pending] = useActionState(ACTIONS[mode], INITIAL_AUTH_STATE);
  const needsPassword = mode === "login" || mode === "signup" || mode === "update";
  const needsEmail = mode !== "update";

  if (EMAIL_TAKEOVER_MODES.has(mode) && state.status === "success") {
    return (
      <section className="auth-card" aria-labelledby="auth-title">
        <p className="eyebrow">Scrooner account</p>
        <h1 id="auth-title">Check your email</h1>
        <StatusPanel className="auth-success" tone="positive" title="On its way">{state.message}</StatusPanel>
        <div className="auth-card__links auth-card__links--center">
          <Link href="/login">Back to sign in</Link>
        </div>
      </section>
    );
  }

  return (
    <section className="auth-card" aria-labelledby="auth-title">
      <p className="eyebrow">Scrooner account</p>
      <h1 id="auth-title">{COPY[mode].title}</h1>
      <p className="auth-card__intro">
        {mode === "login" && "Sign in to keep your research settings tied to your account."}
        {mode === "signup" && "Create an account to keep your Scrooner workspace available across sessions."}
        {mode === "recovery" && "Enter your email and we’ll send a secure link if an account exists."}
        {mode === "update" && "Use a unique password with at least eight characters."}
      </p>

      {OAUTH_MODES.has(mode) && <OAuthButtons redirectUrl={redirectUrl} />}

      <form action={action} className="auth-form" noValidate>
        <input type="hidden" name="redirectUrl" value={redirectUrl} />
        {needsEmail && (
          <Field className="auth-field" htmlFor={`${mode}-email`} label="Email address" error={state.errors?.email} errorId={`${mode}-email-error`}>
            <input className="ds-control" id={`${mode}-email`} name="email" type="email" autoComplete="email" required autoFocus aria-invalid={Boolean(state.errors?.email)} aria-describedby={state.errors?.email ? `${mode}-email-error` : undefined} />
          </Field>
        )}
        {needsPassword && (
          <PasswordField
            id={`${mode}-password`}
            name="password"
            label={mode === "update" ? "New password" : "Password"}
            autoComplete={mode === "login" ? "current-password" : "new-password"}
            hint={mode === "signup" || mode === "update" ? "At least 8 characters." : undefined}
            error={state.errors?.password}
            errorId={`${mode}-password-error`}
            autoFocus={mode === "update"}
          />
        )}
        {(mode === "signup" || mode === "update") && (
          <PasswordField
            id={`${mode}-confirm-password`}
            name="confirmPassword"
            label="Confirm password"
            autoComplete="new-password"
            errorId={`${mode}-password-error`}
            invalid={Boolean(state.errors?.password)}
          />
        )}
        {state.message && <p className={`auth-message auth-message--${state.status}`} role={state.status === "error" ? "alert" : "status"}>{state.message}</p>}
        <Button className="auth-submit" type="submit" loading={pending} loadingLabel="Please wait…">{COPY[mode].submit}</Button>
      </form>

      <div className="auth-card__links">
        {mode === "login" && <><Link href="/forgot-password">Forgot password?</Link><span>New to Scrooner? <Link href="/signup">Create an account</Link></span></>}
        {mode === "signup" && <span>Already have an account? <Link href="/login">Sign in</Link></span>}
        {(mode === "recovery" || mode === "update") && <Link href="/login">Back to sign in</Link>}
      </div>
    </section>
  );
}
