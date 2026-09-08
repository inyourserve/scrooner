import { createBrowserClient } from "@supabase/ssr";

// Deliberately NOT getAuthEnvironmentStatus() here -- it looks up each key
// dynamically (`environment[key]` over an array of names), which Next.js
// can only inline into the browser bundle for a LITERAL `process.env.X`
// expression. In the browser, process.env is empty for anything accessed
// dynamically, so that check always reported "disabled" here even with
// both values set -- invisible until something first called createClient()
// from client-side code (every prior caller was server-only). Reading the
// two literal expressions directly is what Next.js can actually replace.
const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL;
const SUPABASE_PUBLISHABLE_KEY = process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY;

export function createClient() {
  if (!SUPABASE_URL || !SUPABASE_PUBLISHABLE_KEY) {
    throw new Error("Supabase Auth is not configured.");
  }

  return createBrowserClient(SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY);
}
