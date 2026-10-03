import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { SaveScreenButton } from "./SaveScreenButton";
import type { ScreenQueryPayload } from "@/lib/screener/types";
import { savedScreensApi } from "@/lib/saved-screens/client";

const push = vi.fn();
vi.mock("next/navigation", () => ({
  useRouter: () => ({ push }),
}));

vi.mock("@/lib/saved-screens/client", () => ({
  savedScreensApi: { create: vi.fn() },
}));

const query: ScreenQueryPayload = {
  metric_predicates: [{ metric_name: "roe", operator: ">", value: "0.2" }],
  categorical_predicates: [],
  include_inactive: false,
  sort_by: "roe",
  sort_desc: true,
  limit: null,
};

describe("SaveScreenButton", () => {
  afterEach(() => {
    cleanup();
    push.mockReset();
    window.sessionStorage.clear();
  });

  it("saves in a dialog without leaving the query results page", async () => {
    vi.mocked(savedScreensApi.create).mockResolvedValue({ id: 4, name: "Quality", slug: "quality" });
    render(<SaveScreenButton query={query} runId="run-1" />);
    fireEvent.click(screen.getByRole("button", { name: "Save screen" }));

    expect(screen.getByRole("dialog", { name: "Save screen" })).toBeInTheDocument();
    fireEvent.change(screen.getByLabelText("Screen name"), { target: { value: "Quality" } });
    fireEvent.click(screen.getAllByRole("button", { name: "Save screen" })[1]);

    await waitFor(() => expect(savedScreensApi.create).toHaveBeenCalledWith("Quality", query, "run-1"));
    expect(screen.getByRole("dialog", { name: "Screen saved" })).toBeInTheDocument();
    expect(screen.getByText("Your current query results are still here.")).toBeInTheDocument();
    expect(push).not.toHaveBeenCalled();
  });
});
