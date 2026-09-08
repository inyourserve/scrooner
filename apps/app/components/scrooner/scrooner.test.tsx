import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { Delta } from "./Delta";
import { EmptyState } from "./EmptyState";
import { SearchCommand } from "./SearchCommand";
import { StockHeader } from "./StockHeader";
import { TableSkeleton } from "./TableSkeleton";
import { TickerBadge } from "./TickerBadge";

const pushMock = vi.fn();
vi.mock("next/navigation", () => ({ useRouter: () => ({ push: pushMock }) }));

afterEach(cleanup);

describe("Delta", () => {
  it("marks a positive value with the positive tone and an up arrow", () => {
    render(<Delta value={1.24} />);
    const el = screen.getByText("+1.24%");
    expect(el).toHaveClass("ds-delta--positive");
    expect(el.querySelector("svg")).toBeInTheDocument();
  });

  it("marks a negative value with the negative tone and a down arrow", () => {
    render(<Delta value={-2.5} />);
    const el = screen.getByText("-2.50%");
    expect(el).toHaveClass("ds-delta--negative");
  });

  it("falls back to a neutral dash for a missing value, never guessing a tone", () => {
    render(<Delta value={null} />);
    expect(screen.getByText("—")).toHaveClass("ds-delta--neutral");
  });

  it("inverts the tone for metrics where a decrease is favorable", () => {
    render(<Delta value={-3} invert format={(v) => `${v}% debt`} />);
    expect(screen.getByText("-3% debt")).toHaveClass("ds-delta--positive");
  });

  it("can suppress the arrow icon without changing the tone", () => {
    render(<Delta value={1} showIcon={false} />);
    const el = screen.getByText("+1.00%");
    expect(el).toHaveClass("ds-delta--positive");
    expect(el.querySelector("svg")).not.toBeInTheDocument();
  });
});

describe("TickerBadge", () => {
  it("renders the ticker and an optional exchange", () => {
    render(<TickerBadge ticker="AAPL" exchange="NASDAQ" />);
    expect(screen.getByText("AAPL")).toBeInTheDocument();
    expect(screen.getByText("NASDAQ")).toHaveClass("ds-ticker-badge__exchange");
  });

  it("omits the exchange element entirely when none is given", () => {
    const { container } = render(<TickerBadge ticker="JPM" size="sm" />);
    expect(container.querySelector(".ds-ticker-badge__exchange")).not.toBeInTheDocument();
    expect(container.querySelector(".ds-ticker-badge")).toHaveAttribute("data-size", "sm");
  });
});

describe("EmptyState", () => {
  it("is the one shared implementation -- bordered by default for standalone use", () => {
    const { container } = render(<EmptyState description="Nothing here yet." />);
    expect(container.querySelector(".ds-empty-state--bordered")).toBeInTheDocument();
    expect(screen.getByText("Nothing here yet.")).toBeInTheDocument();
  });

  it("drops its own border when nested inside an already-bordered container", () => {
    const { container } = render(<EmptyState description="No matches." bordered={false} />);
    expect(container.querySelector(".ds-empty-state--bordered")).not.toBeInTheDocument();
    expect(container.querySelector(".ds-empty-state")).toBeInTheDocument();
  });

  it("renders an optional icon mark, title, and action together", () => {
    render(<EmptyState icon="0" title="No matches" description="Loosen a filter." action={<button type="button">Edit</button>} />);
    expect(screen.getByText("0")).toHaveClass("ds-empty-state__mark");
    expect(screen.getByRole("heading", { name: "No matches" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Edit" })).toBeInTheDocument();
  });
});

describe("TableSkeleton", () => {
  it("renders the real column headers so there is zero layout shift once results arrive", () => {
    render(<TableSkeleton columnLabels={["ROE", "Revenue growth"]} />);
    expect(screen.getByRole("columnheader", { name: "ROE" })).toBeInTheDocument();
    expect(screen.getByRole("columnheader", { name: "Revenue growth" })).toBeInTheDocument();
  });

  it("renders the requested number of placeholder rows and hides only the decorative shimmer from the accessibility tree", () => {
    const { container } = render(<TableSkeleton columnLabels={["ROE"]} rows={3} />);
    expect(container.querySelectorAll("tbody tr")).toHaveLength(3);
    expect(container.querySelector("tbody")).toHaveAttribute("aria-hidden", "true");
    expect(screen.getByRole("columnheader", { name: "ROE" })).toBeInTheDocument();
  });
});

describe("StockHeader", () => {
  it("renders the ticker, name, and status for every company the same way", () => {
    render(<StockHeader ticker="AAPL" companyName="Apple Inc." sector="Technology" status="active" price={null} dayChangePct={null} dayChangeAbs={null} />);
    expect(screen.getByRole("heading", { name: "AAPL Apple Inc." })).toBeInTheDocument();
    expect(screen.getByText("active")).toHaveClass("ds-badge--positive");
  });

  it("shows an honest dash, never a guessed price, when there is no verified price", () => {
    render(<StockHeader ticker="AAPL" companyName="Apple Inc." sector={null} status="active" price={null} dayChangePct={null} dayChangeAbs={null} />);
    expect(screen.getByText("No verified market price on record")).toBeInTheDocument();
  });

  it("renders the price and a signed day change when a verified price exists", () => {
    render(<StockHeader ticker="AAPL" companyName="Apple Inc." sector={null} status="active" price={{ value: 309.69, asOfLabel: "Aug 21, 2026, 7:59 PM" }} dayChangePct={1.88} dayChangeAbs={5.72} />);
    expect(screen.getByText("$309.69")).toBeInTheDocument();
    expect(screen.getByText("+$5.72 (+1.88%) today")).toHaveClass("ds-delta--positive");
  });

  it("only shows the official-website action when a website is actually on file", () => {
    const { rerender } = render(<StockHeader ticker="AAPL" companyName="Apple Inc." sector={null} status="active" price={null} dayChangePct={null} dayChangeAbs={null} />);
    expect(screen.queryByRole("link", { name: /Official website/ })).not.toBeInTheDocument();

    rerender(<StockHeader ticker="AAPL" companyName="Apple Inc." sector={null} status="active" price={null} dayChangePct={null} dayChangeAbs={null} website="apple.com" />);
    expect(screen.getByRole("link", { name: /Official website/ })).toHaveAttribute("href", "https://apple.com");
  });
});

describe("SearchCommand", () => {
  beforeEach(() => {
    localStorage.clear();
    pushMock.mockClear();
    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.startsWith("/api/company-search")) {
        return { ok: true, json: async () => ({ companies: [{ ticker: "AAPL", company_name: "Apple Inc.", exchange: "NASDAQ", sector: "Technology" }] }) } as Response;
      }
      throw new Error(`Unexpected request: ${url}`);
    }));
  });

  it("opens on Cmd+K and closes on Escape, same contract as every other dialog", () => {
    render(<SearchCommand />);
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();

    fireEvent.keyDown(document, { key: "k", metaKey: true });
    expect(screen.getByRole("dialog", { name: "Search" })).toBeInTheDocument();

    fireEvent.keyDown(document, { key: "Escape" });
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });

  it("opens from the visible trigger button too, not just the keyboard shortcut", () => {
    render(<SearchCommand />);
    fireEvent.click(screen.getByRole("button", { name: /Search companies or tickers/ }));
    expect(screen.getByRole("dialog", { name: "Search" })).toBeInTheDocument();
  });

  it("searches as you type and navigates to the selected company", async () => {
    render(<SearchCommand />);
    fireEvent.click(screen.getByRole("button", { name: /Search companies or tickers/ }));

    fireEvent.change(screen.getByPlaceholderText("Search companies, tickers…"), { target: { value: "aapl" } });
    fireEvent.click(await screen.findByRole("option", { name: /Apple Inc\./ }));

    expect(pushMock).toHaveBeenCalledWith("/stocks/aapl");
    await waitFor(() => expect(screen.queryByRole("dialog")).not.toBeInTheDocument());
  });
});
