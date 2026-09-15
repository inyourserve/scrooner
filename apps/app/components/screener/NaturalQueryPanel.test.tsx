import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { NaturalQueryPanel } from "./NaturalQueryPanel";

const push = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push, prefetch: vi.fn() }),
}));

describe("NaturalQueryPanel navigation mode", () => {
  afterEach(() => {
    cleanup();
    push.mockReset();
    vi.restoreAllMocks();
    vi.unstubAllGlobals();
  });

  it("navigates immediately with a reserved run id while the run is created", async () => {
    vi.spyOn(globalThis.crypto, "randomUUID").mockReturnValue("00000000-0000-4000-8000-000000000001");
    const fetchMock = vi.fn().mockResolvedValue(Response.json({
      run_id: "run-1",
      query_text: "ROE above 20%",
      normalized_query: { sort_by: "roe", sort_desc: true },
    }));
    vi.stubGlobal("fetch", fetchMock);
    render(<NaturalQueryPanel metrics={[]} submitPath="/app/screens/new/raw" />);

    fireEvent.change(screen.getByRole("textbox", { name: "Your criteria" }), {
      target: { value: "ROE above 20%" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Show matches" }));

    await waitFor(() => expect(push).toHaveBeenCalledWith(
      "/app/screens/new/raw?query=ROE+above+20%25&run=00000000-0000-4000-8000-000000000001&page=1&limit=50",
      { scroll: true },
    ));
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it("runs a query supplied by the raw route automatically", async () => {
    const onRunCreated = vi.fn();
    const run = { run_id: "run-1", query_text: "ROE above 20%" };
    const fetchMock = vi.fn().mockResolvedValue(Response.json(run));
    vi.stubGlobal("fetch", fetchMock);

    render(
      <NaturalQueryPanel
        metrics={[]}
        initialText="ROE above 20%"
        autoRun
        onRunCreated={onRunCreated}
      />,
    );

    await waitFor(() => expect(onRunCreated).toHaveBeenCalledWith(run));
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });
});
