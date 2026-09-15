import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { SaveScreenButton, SAVE_QUERY_SESSION_KEY } from "./SaveScreenButton";
import type { ScreenQueryPayload } from "@/lib/screener/types";

const push = vi.fn();
vi.mock("next/navigation", () => ({
  usePathname: () => "/app/screens/new/raw",
  useRouter: () => ({ push }),
  useSearchParams: () => new URLSearchParams("query=ROE+above+20%25&run=run-1&limit=10&page=1"),
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

  it("opens a dedicated save page while preserving the run and query", () => {
    render(<SaveScreenButton query={query} runId="run-1" />);
    fireEvent.click(screen.getByRole("button", { name: "Save screen" }));

    expect(JSON.parse(window.sessionStorage.getItem(`${SAVE_QUERY_SESSION_KEY}:run-1`) || "null")).toEqual(query);
    expect(push).toHaveBeenCalledWith(expect.stringMatching(/^\/app\/screens\/new\/save\?/));
    expect(push.mock.calls[0][0]).toContain("run=run-1");
    expect(push.mock.calls[0][0]).toContain("query=ROE+above+20%25");
  });
});
