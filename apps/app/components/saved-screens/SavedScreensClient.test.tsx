import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { SavedScreensClient } from "./SavedScreensClient";

vi.mock("next/navigation", () => ({ useRouter: () => ({ push: vi.fn() }) }));
vi.mock("@/lib/supabase/client", () => ({
  createClient: () => ({ auth: { getSession: async () => ({ data: { session: { access_token: "token" } } }) } }),
}));

afterEach(() => { vi.restoreAllMocks(); vi.unstubAllGlobals(); });

describe("SavedScreensClient", () => {
  it("loads, renames, and confirms before deleting a saved screen", async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(new Response(JSON.stringify({ id: 7, name: "High quality" }), { status: 200 }))
      .mockResolvedValueOnce(new Response(JSON.stringify({ deleted: 7 }), { status: 200 }));
    vi.stubGlobal("fetch", fetchMock);
    render(<SavedScreensClient initialScreens={[{ id: 7, name: "Quality", slug: "quality", query: { metric_predicates: [{ metric_name: "roe", operator: ">", value: "20" }], categorical_predicates: [], include_inactive: false, sort_by: "roe", sort_desc: true, limit: 50 }, created_at: "2026-08-01", updated_at: "2026-08-02" }]} />);
    expect(screen.getByText("Quality")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Rename" }));
    fireEvent.change(screen.getByLabelText("Screen name"), { target: { value: "High quality" } });
    fireEvent.click(within(screen.getByRole("dialog")).getByRole("button", { name: "Save name" }));
    expect(await screen.findByText("High quality")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Delete" }));
    expect(screen.getByRole("alertdialog")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Delete screen" }));
    await waitFor(() => expect(screen.queryByText("High quality")).not.toBeInTheDocument());
  });
});
