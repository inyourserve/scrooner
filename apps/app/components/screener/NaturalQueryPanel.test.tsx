import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { NaturalQueryPanel } from "./NaturalQueryPanel";
import { __resetNlVocabularyCacheForTests } from "@/lib/screener/suggest";
import type { MetricDefinition } from "@/lib/screener/types";

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
    __resetNlVocabularyCacheForTests();
  });

  function stubFetch(screenRunResponse: unknown) {
    // Every render also fires one harmless, fire-and-forget fetch for the
    // create-screen suggestion vocabulary (2026-10-02, lib/screener/
    // suggest.ts) -- stubbed here with an empty vocabulary so these tests
    // assert against the one call that actually matters (the screen run),
    // not an incidental count.
    const fetchMock = vi.fn((input: RequestInfo | URL) => {
      if (String(input) === "/api/nl-vocabulary") {
        return Promise.resolve(Response.json({ metrics: [], operators: [], sectors: [] }));
      }
      return Promise.resolve(Response.json(screenRunResponse));
    });
    vi.stubGlobal("fetch", fetchMock);
    return fetchMock;
  }

  function screenRunCalls(fetchMock: ReturnType<typeof vi.fn>) {
    return fetchMock.mock.calls.filter(([input]) => String(input) !== "/api/nl-vocabulary");
  }

  it("navigates immediately with a reserved run id while the run is created", async () => {
    vi.spyOn(globalThis.crypto, "randomUUID").mockReturnValue("00000000-0000-4000-8000-000000000001");
    const fetchMock = stubFetch({
      run_id: "run-1",
      query_text: "ROE above 20%",
      normalized_query: { sort_by: "roe", sort_desc: true },
    });
    render(<NaturalQueryPanel metrics={[]} submitPath="/app/screens/new/raw" />);

    fireEvent.change(screen.getByRole("textbox", { name: "Your criteria" }), {
      target: { value: "ROE above 20%" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Show matches" }));

    await waitFor(() => expect(push).toHaveBeenCalledWith(
      "/app/screens/new/raw?query=ROE+above+20%25&run=00000000-0000-4000-8000-000000000001&page=1&limit=50",
      { scroll: true },
    ));
    expect(screenRunCalls(fetchMock)).toHaveLength(1);
  });

  it("runs a query supplied by the raw route automatically", async () => {
    const onRunCreated = vi.fn();
    const run = { run_id: "run-1", query_text: "ROE above 20%" };
    const fetchMock = stubFetch(run);

    render(
      <NaturalQueryPanel
        metrics={[]}
        initialText="ROE above 20%"
        autoRun
        onRunCreated={onRunCreated}
      />,
    );

    await waitFor(() => expect(onRunCreated).toHaveBeenCalledWith(run));
    expect(screenRunCalls(fetchMock)).toHaveLength(1);
  });
});

describe("NaturalQueryPanel typeahead", () => {
  afterEach(() => {
    cleanup();
    vi.restoreAllMocks();
    vi.unstubAllGlobals();
    __resetNlVocabularyCacheForTests();
  });

  const vocabulary = {
    metrics: [
      { phrase: "return on equity", metric_names: ["roe"] },
      { phrase: "return on invested capital", metric_names: ["roic"] },
    ],
    operators: [{ phrase: "above", operator: ">" }],
    sectors: [],
  };

  const roeMetric = {
    metric_name: "roe",
    display_name: "Return on equity (ROE)",
    short_definition: "Net income relative to stockholders' equity.",
    formula_description: "Net Income / Stockholders' Equity",
    formula_version: 1,
    category: "Returns",
    value_type: "percentage" as const,
    operators: [">", "<"] as MetricDefinition["operators"],
  };

  function stubVocabulary() {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(Response.json(vocabulary)));
  }

  it("shows matching metric suggestions as the user types a prefix, then inserts the full phrase on click", async () => {
    stubVocabulary();
    render(<NaturalQueryPanel metrics={[roeMetric]} />);
    const input = screen.getByRole("textbox", { name: "Your criteria" }) as HTMLTextAreaElement;

    fireEvent.change(input, { target: { value: "re" } });
    input.selectionStart = input.selectionEnd = 2;
    fireEvent.select(input);

    const option = await screen.findByRole("option", { name: /Return on equity/ });
    expect(screen.getByRole("option", { name: /Return on invested capital/i })).toBeInTheDocument();

    fireEvent.click(option);

    await waitFor(() => expect(input.value).toBe("return on equity "));
    expect(screen.queryByRole("listbox")).not.toBeInTheDocument();
  });

  it("matches an operator by the last word after an already-typed metric", async () => {
    stubVocabulary();
    render(<NaturalQueryPanel metrics={[roeMetric]} />);
    const input = screen.getByRole("textbox", { name: "Your criteria" }) as HTMLTextAreaElement;

    fireEvent.change(input, { target: { value: "roe ab" } });
    input.selectionStart = input.selectionEnd = 6;
    fireEvent.select(input);

    const option = await screen.findByRole("option", { name: /above/i });
    fireEvent.click(option);

    await waitFor(() => expect(input.value).toBe("roe above "));
  });

  it("accepts the active suggestion with Enter", async () => {
    stubVocabulary();
    render(<NaturalQueryPanel metrics={[roeMetric]} />);
    const input = screen.getByRole("textbox", { name: "Your criteria" }) as HTMLTextAreaElement;

    fireEvent.change(input, { target: { value: "re" } });
    input.selectionStart = input.selectionEnd = 2;
    fireEvent.select(input);
    await screen.findByRole("listbox");

    fireEvent.keyDown(input, { key: "Enter" });

    await waitFor(() => expect(input.value).toBe("return on equity "));
    expect(screen.queryByRole("listbox")).not.toBeInTheDocument();
  });

  it("closes the dropdown with Escape without changing the text", async () => {
    stubVocabulary();
    render(<NaturalQueryPanel metrics={[roeMetric]} />);
    const input = screen.getByRole("textbox", { name: "Your criteria" }) as HTMLTextAreaElement;

    fireEvent.change(input, { target: { value: "re" } });
    input.selectionStart = input.selectionEnd = 2;
    fireEvent.select(input);
    await screen.findByRole("listbox");

    fireEvent.keyDown(input, { key: "Escape" });

    expect(screen.queryByRole("listbox")).not.toBeInTheDocument();
    expect(input.value).toBe("re");
  });

  it("never shows a suggestion for text that matches nothing in the vocabulary", async () => {
    stubVocabulary();
    render(<NaturalQueryPanel metrics={[roeMetric]} />);
    const input = screen.getByRole("textbox", { name: "Your criteria" }) as HTMLTextAreaElement;

    fireEvent.change(input, { target: { value: "xyzzy" } });
    input.selectionStart = input.selectionEnd = 5;
    fireEvent.select(input);

    await waitFor(() => expect(screen.queryByRole("listbox")).not.toBeInTheDocument());
  });
});
