import { cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { ScreenerClient } from "./ScreenerClient";
import type { AskResponse, MetricDefinition, ScreenQueryPayload, ScreenResult } from "@/lib/screener/types";

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
      if (path === "/api/ask") {
        const body = JSON.parse(String(init?.body)) as { text: string; run: boolean };
        return Promise.resolve(response(askHandler ? askHandler(body) : askPayload, askOk, askStatus));
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

  it("blocks an empty screen before making a screen request", async () => {
    render(<ScreenerClient siteUrl="https://scrooner.example" />);
    await screen.findByRole("button", { name: "Run screen" });
    fireEvent.click(screen.getByRole("button", { name: "Remove condition 1" }));
    fireEvent.click(screen.getByRole("button", { name: "Run screen" }));

    expect(await screen.findByText("Add at least one metric or company classification.")).toBeInTheDocument();
    expect(fetch).toHaveBeenCalledTimes(1);
  });

  it("distinguishes a successful zero-result screen from an error", async () => {
    render(<ScreenerClient siteUrl="https://scrooner.example" />);
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
    fireEvent.click(await screen.findByRole("button", { name: "Run screen" }));

    expect(await screen.findByText("AAPL")).toBeInTheDocument();
    expect(screen.getByText("42.3%")).toHaveAttribute("title", "Exact value: 0.4234567890123456789012345678");
    expect(screen.getByText("TTM · 2026-06-30 · v1")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /AAPL Apple Inc\./ })).toHaveAttribute("href", "https://scrooner.example/stock/aapl/");
    expect(screen.getByRole("link", { name: "Return on equity (ROE)" })).toHaveAttribute("href", "#definition-roe");
    expect(screen.getByRole("heading", { name: "Metric definitions used" })).toBeInTheDocument();
    expect(screen.getByText(/1 company was excluded for missing data/)).toBeInTheDocument();
    fireEvent.click(screen.getByText("Why matched"));
    expect(screen.getByText(/Matched at 42.3% · TTM · 2026-06-30 · formula v1/)).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /Open company filings and source context/ })).toHaveAttribute("href", "https://scrooner.example/stock/aapl/");
  });

  it("preserves criteria and presents an API failure separately", async () => {
    screenPayload = { detail: "Screening service unavailable." };
    screenOk = false;
    screenStatus = 502;
    render(<ScreenerClient siteUrl="https://scrooner.example" />);
    fireEvent.click(await screen.findByRole("button", { name: "Run screen" }));

    expect(await screen.findByText("The screen did not run")).toBeInTheDocument();
    expect(screen.getByText("Screening service unavailable.")).toBeInTheDocument();
    expect(screen.getByDisplayValue("30")).toBeInTheDocument();
  });

  it("shows a named loading state while a screen is running", async () => {
    let resolveRequest: (value: Response) => void = () => undefined;
    screenRequest = new Promise<Response>((resolve) => { resolveRequest = resolve; });
    render(<ScreenerClient siteUrl="https://scrooner.example" />);
    fireEvent.click(await screen.findByRole("button", { name: "Run screen" }));

    expect(await screen.findByText("Running your screen")).toBeInTheDocument();
    resolveRequest(response(emptyResult));
    await waitFor(() => expect(screen.getByText("No companies matched every criterion")).toBeInTheDocument());
  });

  it("interprets supported language without executing and transfers it for deliberate review", async () => {
    render(<ScreenerClient siteUrl="https://scrooner.example" />);
    const input = await screen.findByRole("textbox", { name: "Screening request" });
    fireEvent.change(input, { target: { value: "companies with ROE above 30%" } });
    fireEvent.click(screen.getByRole("button", { name: "Interpret query" }));

    expect(await screen.findByText("Ready for your review")).toBeInTheDocument();
    expect(screen.getByText(/Nothing has been executed\./)).toBeInTheDocument();
    const interpretedCriteria = screen.getByRole("table", { name: "Interpreted criteria" });
    expect(within(interpretedCriteria).getByText("Greater than")).toBeInTheDocument();
    expect(within(interpretedCriteria).getByText("30%")).toBeInTheDocument();
    expect(vi.mocked(fetch).mock.calls.filter(([path]) => String(path) === "/api/screen")).toHaveLength(0);

    fireEvent.click(screen.getByRole("button", { name: "Review and edit criteria" }));
    expect(await screen.findByText("Interpreted criteria are ready to review")).toBeInTheDocument();
    expect(screen.getByDisplayValue("30")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Run screen" }));
    expect(await screen.findByText("No companies matched every criterion")).toBeInTheDocument();
    const askCall = vi.mocked(fetch).mock.calls.find(([path]) => String(path) === "/api/ask");
    expect(JSON.parse(String(askCall?.[1]?.body))).toEqual({ text: "companies with ROE above 30%", run: false });
  });

  it("shows ambiguity choices and never executes before the choice is reinterpreted", async () => {
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
    const input = await screen.findByRole("textbox", { name: "Screening request" });
    fireEvent.change(input, { target: { value: "revenue growth above 10%" } });
    fireEvent.click(screen.getByRole("button", { name: "Interpret query" }));

    expect(await screen.findByText("Resolve the language before running")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Review and edit criteria" })).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Revenue growth (YoY)" }));
    expect(await screen.findByText("Ready for your review")).toBeInTheDocument();
    expect(input).toHaveValue("revenue growth yoy above 10%");
    expect(vi.mocked(fetch).mock.calls.filter(([path]) => String(path) === "/api/screen")).toHaveLength(0);
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
    const input = await screen.findByRole("textbox", { name: "Screening request" });
    fireEvent.change(input, { target: { value: "roe above 20% and magic number below 5" } });
    fireEvent.click(screen.getByRole("button", { name: "Interpret query" }));

    expect(await screen.findByRole("heading", { name: "Recognized criteria" })).toBeInTheDocument();
    expect(screen.getByText("“magic number below 5”")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Review and edit criteria" })).not.toBeInTheDocument();
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
    const input = await screen.findByRole("textbox", { name: "Screening request" });
    fireEvent.change(input, { target: { value: "companies with a magic number over 5" } });
    fireEvent.click(screen.getByRole("button", { name: "Interpret query" }));

    expect(await screen.findByText("“companies with a magic number over 5”")).toBeInTheDocument();
    expect(input).toHaveValue("companies with a magic number over 5");
    expect(screen.queryByRole("button", { name: "Review and edit criteria" })).not.toBeInTheDocument();
  });
});
