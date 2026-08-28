"use server";

import { redirect } from "next/navigation";
import { getAuthEnvironmentStatus } from "@/lib/auth/config";
import { getSafeRedirectPath } from "@/lib/auth/redirect";
import type { AuthActionState } from "@/lib/auth/state";
import { createClient } from "@/lib/supabase/server";

function unavailable(): AuthActionState | null {
  return getAuthEnvironmentStatus().enabled
    ? null
    : {
        status: "error",
        message:
          "Account access is not configured in this environment. Add the public Supabase Auth settings to continue.",
      };
}

function credentials(formData: FormData, options?: { confirm?: boolean }) {
  const email = String(formData.get("email") || "").trim().toLowerCase();
  const password = String(formData.get("password") || "");
  const errors: AuthActionState["errors"] = {};

  if (!/^\S+@\S+\.\S+$/.test(email)) errors.email = "Enter a valid email address.";
  if (password.length < 8) errors.password = "Use at least 8 characters.";
  if (options?.confirm && password !== String(formData.get("confirmPassword") || "")) {
    errors.password = "Passwords do not match.";
  }

  return { email, password, errors };
}

export async function login(
  _state: AuthActionState,
  formData: FormData,
): Promise<AuthActionState> {
  const disabled = unavailable();
  if (disabled) return disabled;

  const { email, password, errors } = credentials(formData);
  if (Object.keys(errors).length) return { status: "error", errors };

  const supabase = await createClient();
  const { error } = await supabase.auth.signInWithPassword({ email, password });
  if (error) {
    return { status: "error", message: "Email or password is incorrect." };
  }

  redirect(getSafeRedirectPath(String(formData.get("redirectUrl") || "")));
}

export async function signup(
  _state: AuthActionState,
  formData: FormData,
): Promise<AuthActionState> {
  const disabled = unavailable();
  if (disabled) return disabled;

  const { email, password, errors } = credentials(formData, { confirm: true });
  if (Object.keys(errors).length) return { status: "error", errors };

  const appUrl = process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000";
  const supabase = await createClient();
  const { data, error } = await supabase.auth.signUp({
    email,
    password,
    options: { emailRedirectTo: `${appUrl.replace(/\/$/, "")}/auth/callback` },
  });

  if (error) return { status: "error", message: error.message };
  if (data.session) redirect("/account");

  return {
    status: "success",
    message: "Check your email to confirm your account, then sign in.",
  };
}

export async function requestPasswordReset(
  _state: AuthActionState,
  formData: FormData,
): Promise<AuthActionState> {
  const disabled = unavailable();
  if (disabled) return disabled;

  const email = String(formData.get("email") || "").trim().toLowerCase();
  if (!/^\S+@\S+\.\S+$/.test(email)) {
    return { status: "error", errors: { email: "Enter a valid email address." } };
  }

  const appUrl = process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000";
  const supabase = await createClient();
  const { error } = await supabase.auth.resetPasswordForEmail(email, {
    redirectTo: `${appUrl.replace(/\/$/, "")}/auth/callback?next=/account/update-password`,
  });

  if (error) return { status: "error", message: "We could not send the reset email. Try again shortly." };
  return {
    status: "success",
    message: "If an account exists for that email, a password reset link is on its way.",
  };
}

export async function updatePassword(
  _state: AuthActionState,
  formData: FormData,
): Promise<AuthActionState> {
  const disabled = unavailable();
  if (disabled) return disabled;

  const password = String(formData.get("password") || "");
  if (password.length < 8) {
    return { status: "error", errors: { password: "Use at least 8 characters." } };
  }
  if (password !== String(formData.get("confirmPassword") || "")) {
    return { status: "error", errors: { password: "Passwords do not match." } };
  }

  const supabase = await createClient();
  const { error } = await supabase.auth.updateUser({ password });
  return error
    ? { status: "error", message: "We could not update your password. Request a new reset link and try again." }
    : { status: "success", message: "Your password has been updated." };
}

export async function logout() {
  if (getAuthEnvironmentStatus().enabled) {
    const supabase = await createClient();
    await supabase.auth.signOut();
  }
  redirect("/login");
}
