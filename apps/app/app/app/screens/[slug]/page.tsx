import type { Metadata } from "next";
import { notFound, redirect } from "next/navigation";
import { SavedScreenDetailClient } from "@/components/saved-screens/SavedScreenDetailClient";
import { backendUrl } from "@/lib/backend";
import { buildLoginHref } from "@/lib/auth/redirect";
import { createClient } from "@/lib/supabase/server";
import type { SavedScreen } from "@/lib/saved-screens/types";

export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "Saved screen — Scrooner" };

export default async function SavedScreenPage({
  params,
  searchParams,
}: {
  params: Promise<{ slug: string }>;
  searchParams: Promise<{ cursor?: string; page?: string }>;
}) {
  const { slug } = await params;
  const query = await searchParams;
  const supabase = await createClient();
  const { data } = await supabase.auth.getSession();
  if (!data.session?.access_token) redirect(buildLoginHref(`/app/screens/${slug}`));

  const search = new URLSearchParams({ page_size: "50" });
  if (query.cursor) search.set("cursor", query.cursor);
  const response = await fetch(backendUrl(`/v1/screens/${encodeURIComponent(slug)}?${search}`), {
    cache: "no-store",
    headers: { accept: "application/json", authorization: `Bearer ${data.session.access_token}` },
  });
  if (response.status === 404) notFound();
  if (!response.ok) throw new Error("Saved screen could not be loaded.");
  const screen = await response.json() as SavedScreen;
  return <SavedScreenDetailClient initialScreen={screen} initialPage={Math.max(1, Number(query.page) || 1)} />;
}
