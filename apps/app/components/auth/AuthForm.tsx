"use client";

import Link from "next/link";
import { useActionState } from "react";
import {
  login,
  requestPasswordReset,
  signup,
  updatePassword,
} from "@/app/auth/actions";
import { INITIAL_AUTH_STATE, type AuthActionState } from "@/lib/auth/state";

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

export function AuthForm({ mode, redirectUrl = "/screener" }: { mode: Mode; redirectUrl?: string }) {
  const [state, action, pending] = useActionState(ACTIONS[mode], INITIAL_AUTH_STATE);
  const needsPassword = mode === "login" || mode === "signup" || mode === "update";
  const needsEmail = mode !== "update";

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

      <form action={action} className="auth-form" noValidate>
        <input type="hidden" name="redirectUrl" value={redirectUrl} />
        {needsEmail && (
          <div className="auth-field">
            <label htmlFor={`${mode}-email`}>Email address</label>
            <input id={`${mode}-email`} name="email" type="email" autoComplete="email" required aria-invalid={Boolean(state.errors?.email)} aria-describedby={state.errors?.email ? `${mode}-email-error` : undefined} />
            {state.errors?.email && <p className="auth-field__error" id={`${mode}-email-error`}>{state.errors.email}</p>}
          </div>
        )}
        {needsPassword && (
          <div className="auth-field">
            <label htmlFor={`${mode}-password`}>{mode === "update" ? "New password" : "Password"}</label>
            <input id={`${mode}-password`} name="password" type="password" autoComplete={mode === "login" ? "current-password" : "new-password"} minLength={8} required aria-invalid={Boolean(state.errors?.password)} aria-describedby={state.errors?.password ? `${mode}-password-error` : undefined} />
          </div>
        )}
        {(mode === "signup" || mode === "update") && (
          <div className="auth-field">
            <label htmlFor={`${mode}-confirm-password`}>Confirm password</label>
            <input id={`${mode}-confirm-password`} name="confirmPassword" type="password" autoComplete="new-password" minLength={8} required aria-invalid={Boolean(state.errors?.password)} aria-describedby={state.errors?.password ? `${mode}-password-error` : undefined} />
            {state.errors?.password && <p className="auth-field__error" id={`${mode}-password-error`}>{state.errors.password}</p>}
          </div>
        )}
        {mode === "login" && state.errors?.password && <p className="auth-field__error" id="login-password-error">{state.errors.password}</p>}
        {state.message && <p className={`auth-message auth-message--${state.status}`} role={state.status === "error" ? "alert" : "status"}>{state.message}</p>}
        <button className="primary-button auth-submit" type="submit" disabled={pending} aria-disabled={pending}>
          {pending ? "Please wait…" : COPY[mode].submit}
        </button>
      </form>

      <div className="auth-card__links">
        {mode === "login" && <><Link href="/forgot-password">Forgot password?</Link><span>New to Scrooner? <Link href="/signup">Create an account</Link></span></>}
        {mode === "signup" && <span>Already have an account? <Link href="/login">Sign in</Link></span>}
        {(mode === "recovery" || mode === "update") && <Link href="/login">Back to sign in</Link>}
      </div>
    </section>
  );
}
