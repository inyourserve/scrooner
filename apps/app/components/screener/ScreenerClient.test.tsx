import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { ScreenerClient } from "./ScreenerClient";
import { NATURAL_QUERY_EXAMPLES } from "@/lib/screener/interpretation";
import type { AskResponse, MetricDefinition, ScreenQueryPayload, ScreenResult } from "@/lib/screener/types";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), replace: vi.fn(), prefetch: vi.fn() }),
  useSearchParams: () => new URLSearchParams(),
  usePathname: () => "/app/screens/new/raw",
}));

const metric: MetricDefinition = {
  metric_name: "roe",
  display_name: "Return on equity (ROE)",
  short_definition: "Net income relative to stockholders' equity.",
  formula_description: "Net Income / Stockholders' Equity",
  formula_version: 1,
  category: "Returns",
  value_type: "percentage",
  operators: [">", "<", ">=", "<=", "=", "!=", "between", "top_n", "bottom_n"],
};

const revenueYoy: MetricDefinition = {
  ...metric,
  metric_name: "revenue_growth_yoy",
  display_name: "Revenue growth (YoY)",
  short_definition: "Revenue growth versus the same period last year.",
  formula_description: "Current / Prior - 1",
  category: "Growth",
};

const revenueCagr: MetricDefinition = {
  ...revenueYoy,
  metric_name: "revenue_growth_3y_cagr",
  display_name: "Revenue growth (3Y CAGR)",
  short_definition: "Compound revenue growth over three years.",
};

const metrics = [metric, revenueYoy, revenueCagr];

const roeQuery: ScreenQueryPayload = {
  metric_predicates: [{ metric_name: "roe", operator: ">", value: "0.3", value_range: null, n: null }],
  categorical_predicates: [],
  include_inactive: false,
  sort_by: null,
  sort_desc: true,
  limit: null,
};

function readyInterpretation(query = roeQuery): AskResponse {
  return {
    explanation: "Filtering for recognized criteria.",
    query,
    recognized_query: query,
    unrecognized: [],
    ambiguous: [],
    result: emptyResult,
  };
}

function persistedRun(text: string, interpreted: unknown) {
  const value = interpreted as AskResponse;
  if (!value.query || !value.result) return interpreted;
  return {
    run_id: "11111111-1111-1111-1111-111111111111",
    query_text: text,
    normalized_query: value.query,
    total_count: value.result.matched.length,
    items: value.result.matched,
    excluded_missing_data: value.result.excluded_missing_data,
    excluded_inactive: value.result.excluded_inactive,
    cursor: null,
    next_cursor: null,
    ran_at: "2026-09-09T00:00:00Z",
  };
}

const emptyResult: ScreenResult = {
  matched: [],
  excluded_missing_data: [],
  excluded_inactive: [],
};

function response(payload: unknown, ok = true, status = ok ? 200 : 500) {
  return { ok, status, json: async () => payload } as Response;
}

async function openFilterBuilder() {
  fireEvent.click(await screen.findByRole("button", { name: /Exact filters/ }));
  return screen.findByRole("button", { name: "Run screen" });
}

describe("ScreenerClient", () => {
  let screenPayload: unknown;
  let screenOk: boolean;
  let screenStatus: number;
  let screenRequest: Promise<Response> | null;
  let askPayload: unknown;
  let askOk: boolean;
  let askStatus: number;
  let askHandler: ((body: { text: string; run: boolean }) => unknown) | null;

  beforeEach(() => {
    screenPayload = emptyResult;
    screenOk = true;
    screenStatus = 200;
    screenRequest = null;
    askPayload = readyInterpretation();
    askOk = true;
    askStatus = 200;
    askHandler = null;
    vi.stubGlobal("fetch", vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
      const path = String(input);
      if (path === "/api/metrics") return Promise.resolve(response(metrics));
      if (path === "/api/screen-runs") {
        const body = JSON.parse(String(init?.body)) as { text: string; page_size: number };
        const interpreted = askHandler ? askHandler({ text: body.text, run: true }) : askPayload;
        return Promise.resolve(response(persistedRun(body.text, interpreted), askOk, askStatus));
      }
      if (path === "/api/screen") {
        return screenRequest ?? Promise.resolve(response(screenPayload, screenOk, screenStatus));
      }
      return Promise.reject(new Error(`Unexpected request: ${path}`));
    }));
  });

  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  it("keeps the raw-page query editor inside the results card", () => {
    const { container } = render(
      <ScreenerClient siteUrl="https://scrooner.example" initialMetrics={metrics} resultsFirst />,
    );

    const results = container.querySelector(".results-section");
    expect(results).toContainElement(screen.getByRole("region", { name: "Search query" }));
  });

  it("blocks an empty screen before making a screen request", async () => {
    render(<ScreenerClient siteUrl="https://scrooner.example" />);
    await openFilterBuilder();
    fireEvent.click(screen.getByRole("button", { name: "Remove condition 1" }));
    fireEvent.click(screen.getByRole("button", { name: "Run screen" }));

    expect(await screen.findByText("Add at least one metric or company classification.")).toBeInTheDocument();
    await waitFor(() => expect(screen.getByText("Add at least one metric or company classification.").parentElement).toHaveFocus());
    expect(fetch).toHaveBeenCalledTimes(1);
  });

  it("does not create an abort rejection when route cleanup happens during catalog loading", () => {
    let metricRequest: RequestInit | undefined;
    vi.mocked(fetch).mockImplementationOnce((_input, init) => {
      metricRequest = init;
      return new Promise<Response>(() => undefined);
    });

    const { unmount } = render(<ScreenerClient siteUrl="https://scrooner.example" />);
    unmount();

    expect(metricRequest?.signal).toBeUndefined();
  });

  it("distinguishes a successful zero-result screen from an error", async () => {
    render(<ScreenerClient siteUrl="https://scrooner.example" />);
    await openFilterBuilder();
    fireEvent.click(await screen.findByRole("button", { name: "Run screen" }));

    expect(await screen.findByRole("heading", { name: "No companies matched every criterion" })).toBeInTheDocument();
    expect(screen.queryByText("The screen did not run")).not.toBeInTheDocument();
  });

  it("renders selected values, periods, company links, and partial coverage", async () => {
    const result: ScreenResult = {
      matched: [
        {
          company_id: 1,
          cik: "0000320193",
          company_name: "Apple Inc.",
          sic_code: "3571",
          sic_description: "Electronic Computers",
          status: "active",
          ticker: "AAPL",
          metrics: {
            roe: { value: "0.4234567890123456789012345678", period_label: "TTM", period_end: "2026-06-30", formula_version: 1 },
          },
        },
      ],
      excluded_missing_data: [{ cik: "0000789019", company_name: "Microsoft Corp.", missing_metrics: ["roe"] }],
      excluded_inactive: [],
    };
    screenPayload = result;
    render(<ScreenerClient siteUrl="https://scrooner.example" />);
    await openFilterBuilder();
    fireEvent.click(await screen.findByRole("button", { name: "Run screen" }));

    expect(await screen.findByText("AAPL")).toBeInTheDocument();
    expect(screen.getByText("42.3%")).toHaveAttribute("title", "Exact value: 0.4234567890123456789012345678");
    expect(screen.getByText("TTM · 2026-06-30 · v1")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /AAPL Apple Inc\./ })).toHaveAttribute("href", "https://scrooner.example/stocks/aapl/");
    expect(screen.getByRole("button", { name: /Sort by Return on equity/ })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Metric definitions used" })).toBeInTheDocument();
    expect(screen.getByText(/1 company was excluded for missing data/)).toBeInTheDocument();
    fireEvent.click(screen.getByText("Why matched"));
    expect(screen.getByText(/Matched at 42.3% · TTM · 2026-06-30 · formula v1/)).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /Open company filings and source context/ })).toHaveAttribute("href", "https://scrooner.example/stocks/aapl/");
  });

  it("preserves criteria and presents an API failure separately", async () => {
    screenPayload = { detail: "Screening service unavailable." };
    screenOk = false;
    screenStatus = 502;
    render(<ScreenerClient siteUrl="https://scrooner.example" />);
    await openFilterBuilder();
    fireEvent.click(await screen.findByRole("button", { name: "Run screen" }));

    expect(await screen.findByText("The screen did not run")).toBeInTheDocument();
    expect(screen.getByText("Screening service unavailable.")).toBeInTheDocument();
    expect(screen.getByDisplayValue("30")).toBeInTheDocument();
  });

  it("shows a table skeleton while a screen is running", async () => {
    let resolveRequest: (value: Response) => void = () => undefined;
    screenRequest = new Promise<Response>((resolve) => { resolveRequest = resolve; });
    const { container } = render(<ScreenerClient siteUrl="https://scrooner.example" />);
    await openFilterBuilder();
    fireEvent.click(await screen.findByRole("button", { name: "Run screen" }));

    await waitFor(() => expect(container.querySelector(".results-section")).toHaveAttribute("aria-busy", "true"));
    expect(container.querySelector(".ds-table-skeleton")).toBeInTheDocument();
    resolveRequest(response(emptyResult));
    await waitFor(() => expect(screen.getByText("No companies matched every criterion")).toBeInTheDocument());
  });

  it("turns supported language into verified results with one click", async () => {
    render(<ScreenerClient siteUrl="https://scrooner.example" />);
    const input = await screen.findByRole("textbox", { name: "Your criteria" });
    fireEvent.change(input, { target: { value: "companies with ROE above 30%" } });
    fireEvent.click(screen.getByRole("button", { name: "Show matches" }));

    expect(await screen.findByRole("heading", { name: "No companies matched every criterion" })).toBeInTheDocument();
    expect(vi.mocked(fetch).mock.calls.filter(([path]) => String(path) === "/api/screen")).toHaveLength(0);

    // The query box stays put and ready for the next screen -- there is no
    // separate "editor" view to return to, and no second, independent copy
    // of the query/result rendered by the query panel itself; the results
    // section below (driven by the same run the panel just created) is the
    // one place that reflects what's currently on screen.
    expect(screen.getByRole("textbox", { name: "Your criteria" })).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Run screen" })).not.toBeInTheDocument();

    const resultsHeading = screen.getByRole("heading", { name: "Query results" });
    const builderDisclosure = screen.getByRole("button", { name: /Exact filters/ });
    expect(resultsHeading.compareDocumentPosition(builderDisclosure) & Node.DOCUMENT_POSITION_FOLLOWING).not.toBe(0);
    expect(resultsHeading).toHaveFocus();

    fireEvent.click(screen.getByText("View exact query sent to the Screener"));
    expect(screen.getByText(/"metric_name": "roe"/)).toBeInTheDocument();
    const askCall = vi.mocked(fetch).mock.calls.find(([path]) => String(path) === "/api/screen-runs");
    expect(JSON.parse(String(askCall?.[1]?.body))).toEqual({ text: "companies with ROE above 30%", page_size: 10 });
  });

  it("keeps the query box ready for a second screen immediately after results", async () => {
    render(<ScreenerClient siteUrl="https://scrooner.example" />);
    const input = await screen.findByRole("textbox", { name: "Your criteria" });
    fireEvent.change(input, { target: { value: "companies with ROE above 30%" } });
    fireEvent.click(screen.getByRole("button", { name: "Show matches" }));

    await screen.findByRole("heading", { name: "No companies matched every criterion" });
    expect(screen.getByRole("textbox", { name: "Your criteria" })).toHaveValue("companies with ROE above 30%");
    expect(screen.getByRole("button", { name: "Show matches" })).toBeInTheDocument();
  });

  it("blocks ambiguity and runs automatically after the user chooses a meaning", async () => {
    const ambiguous: AskResponse = {
      explanation: "Ambiguous revenue growth horizon.",
      query: null,
      recognized_query: null,
      unrecognized: [],
      ambiguous: [{ phrase: "revenue growth", candidates: ["revenue_growth_yoy", "revenue_growth_3y_cagr"] }],
    };
    const resolvedQuery: ScreenQueryPayload = {
      ...roeQuery,
      metric_predicates: [{ metric_name: "revenue_growth_yoy", operator: ">", value: "0.1", value_range: null, n: null }],
    };
    askHandler = (body) => body.text.includes("yoy") ? readyInterpretation(resolvedQuery) : ambiguous;
    render(<ScreenerClient siteUrl="https://scrooner.example" />);
    const input = await screen.findByRole("textbox", { name: "Your criteria" });
    fireEvent.change(input, { target: { value: "revenue growth above 10%" } });
    fireEvent.click(screen.getByRole("button", { name: "Show matches" }));

    expect(await screen.findByText("Clarify this screen")).toBeInTheDocument();
    expect(screen.getByText("Choose a meaning to continue.")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Revenue growth (YoY)" }));
    expect(await screen.findByRole("heading", { name: "No companies matched every criterion" })).toBeInTheDocument();
    expect(vi.mocked(fetch).mock.calls.filter(([path]) => String(path) === "/api/screen")).toHaveLength(0);
    const askBodies = vi.mocked(fetch).mock.calls
      .filter(([path]) => String(path) === "/api/screen-runs")
      .map(([, init]) => JSON.parse(String(init?.body)));
    expect(askBodies).toEqual([
      { text: "revenue growth above 10%", page_size: 10 },
      { text: "revenue growth yoy above 10%", page_size: 10 },
    ]);
  });

  it("separates recognized clauses from unsupported language without creating a runnable query", async () => {
    askPayload = {
      explanation: "Could not understand one clause.",
      query: null,
      recognized_query: { ...roeQuery, metric_predicates: [{ metric_name: "roe", operator: ">", value: "0.2", value_range: null, n: null }] },
      unrecognized: ["magic number below 5"],
      ambiguous: [],
    } satisfies AskResponse;
    render(<ScreenerClient siteUrl="https://scrooner.example" />);
    const input = await screen.findByRole("textbox", { name: "Your criteria" });
    fireEvent.change(input, { target: { value: "roe above 20% and magic number below 5" } });
    fireEvent.click(screen.getByRole("button", { name: "Show matches" }));

    expect(await screen.findByRole("heading", { name: "What we understood" })).toBeInTheDocument();
    expect(screen.getByText("“magic number below 5”")).toBeInTheDocument();
    expect(vi.mocked(fetch).mock.calls.filter(([path]) => String(path) === "/api/screen")).toHaveLength(0);
  });

  it("explains fully unsupported language and preserves it for editing", async () => {
    askPayload = {
      explanation: "Unknown metric.",
      query: null,
      recognized_query: null,
      unrecognized: ["companies with a magic number over 5"],
      ambiguous: [],
    } satisfies AskResponse;
    render(<ScreenerClient siteUrl="https://scrooner.example" />);
    const input = await screen.findByRole("textbox", { name: "Your criteria" });
    fireEvent.change(input, { target: { value: "companies with a magic number over 5" } });
    fireEvent.click(screen.getByRole("button", { name: "Show matches" }));

    expect(await screen.findByText("“companies with a magic number over 5”")).toBeInTheDocument();
    expect(input).toHaveValue("companies with a magic number over 5");
  });

  it("runs a plain-language example in one click", async () => {
    render(<ScreenerClient siteUrl="https://scrooner.example" />);

    const examples = await screen.findAllByRole("button", { name: /Run example:/ });
    fireEvent.click(examples[0]);

    expect(await screen.findByRole("heading", { name: "No companies matched every criterion" })).toBeInTheDocument();
    const askCall = vi.mocked(fetch).mock.calls.find(([path]) => String(path) === "/api/screen-runs");
    expect(JSON.parse(String(askCall?.[1]?.body))).toEqual({ text: NATURAL_QUERY_EXAMPLES[0], page_size: 10 });
  });

  it("supports the documented command-enter shortcut without a second click", async () => {
    render(<ScreenerClient siteUrl="https://scrooner.example" />);
    const input = await screen.findByRole("textbox", { name: "Your criteria" });
    fireEvent.change(input, { target: { value: "companies with ROE above 30%" } });
    fireEvent.keyDown(input, { key: "Enter", ctrlKey: true });

    expect(await screen.findByRole("heading", { name: "No companies matched every criterion" })).toBeInTheDocument();
    expect(vi.mocked(fetch).mock.calls.filter(([path]) => String(path) === "/api/screen-runs")).toHaveLength(1);
  });

  it("keeps a late response from replacing a newer plain-language screen", async () => {
    let resolveFirstAsk: (value: Response) => void = () => undefined;
    const firstAsk = new Promise<Response>((resolve) => { resolveFirstAsk = resolve; });
    let askCount = 0;
    vi.mocked(fetch).mockImplementation((input) => {
      const path = String(input);
      if (path === "/api/metrics") return Promise.resolve(response(metrics));
      if (path === "/api/screen-runs") {
        askCount += 1;
        return askCount === 1 ? firstAsk : Promise.resolve(response(persistedRun("second current screen", readyInterpretation())));
      }
      return Promise.reject(new Error(`Unexpected request: ${path}`));
    });

    render(<ScreenerClient siteUrl="https://scrooner.example" />);
    const input = await screen.findByRole("textbox", { name: "Your criteria" });
    fireEvent.change(input, { target: { value: "first slow screen" } });
    fireEvent.click(screen.getByRole("button", { name: "Show matches" }));
    fireEvent.change(input, { target: { value: "second current screen" } });
    fireEvent.click(screen.getByRole("button", { name: "Show matches" }));

    expect(await screen.findByText("From “second current screen”")).toBeInTheDocument();
    resolveFirstAsk(response(readyInterpretation()));
    await waitFor(() => expect(screen.queryByText("From “first slow screen”")).not.toBeInTheDocument());
    expect(screen.getByText("From “second current screen”")).toBeInTheDocument();
  });

  it("offers an in-place retry after a structured screen request fails", async () => {
    screenPayload = { detail: "Screening service unavailable." };
    screenOk = false;
    screenStatus = 502;
    render(<ScreenerClient siteUrl="https://scrooner.example" />);
    await openFilterBuilder();
    fireEvent.click(screen.getByRole("button", { name: "Run screen" }));

    const retry = await screen.findByRole("button", { name: "Try again" });
    screenPayload = emptyResult;
    screenOk = true;
    screenStatus = 200;
    fireEvent.click(retry);

    expect(await screen.findByRole("heading", { name: "No companies matched every criterion" })).toBeInTheDocument();
    expect(vi.mocked(fetch).mock.calls.filter(([path]) => String(path) === "/api/screen")).toHaveLength(2);
  });
});
