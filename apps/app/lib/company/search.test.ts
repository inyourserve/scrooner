import { describe, expect, it } from "vitest";
import { addRecentCompany, normalizeCompanyQuery, normalizeRecentCompanies, rankCompanyMatches, type SearchCompany } from "./search";
const apple: SearchCompany = { ticker: "AAPL", company_name: "Apple Inc.", exchange: "Nasdaq", sector: "Technology" };
describe("company search", () => {
  it("normalizes and caps queries", () => { expect(normalizeCompanyQuery("  Apple   Inc.  ")).toBe("apple inc."); expect(normalizeCompanyQuery("x".repeat(80))).toHaveLength(64); });
  it("validates, deduplicates, and caps recent companies", () => { const result = normalizeRecentCompanies([apple, apple, ...["MSFT", "NVDA", "AMZN", "COST", "JPM"].map((ticker) => ({ ticker, company_name: ticker, exchange: null, sector: null }))]); expect(result.map((item) => item.ticker)).toEqual(["AAPL", "MSFT", "NVDA", "AMZN", "COST"]); });
  it("moves a selection to the front", () => { const msft = { ...apple, ticker: "MSFT", company_name: "Microsoft" }; expect(addRecentCompany([apple, msft], msft).map((item) => item.ticker)).toEqual(["MSFT", "AAPL"]); });
});

describe("rankCompanyMatches", () => {
  const directory: SearchCompany[] = [
    apple,
    { ticker: "V", company_name: "Visa Inc.", exchange: "NYSE", sector: "Financials" },
    { ticker: "VZ", company_name: "Verizon Communications Inc", exchange: "NYSE", sector: "Telecom" },
    { ticker: "AAPI", company_name: "Apple iSports Group, Inc.", exchange: null, sector: "Other" },
    { ticker: "MU", company_name: "Micron Technology, Inc.", exchange: "Nasdaq", sector: "Technology" },
  ];

  it("ranks an exact ticker match first, ahead of a name/ticker prefix match", () => {
    expect(rankCompanyMatches(directory, "v").map((c) => c.ticker)).toEqual(["V", "VZ"]);
  });

  it("ranks ticker-prefix matches over a name-prefix-only match, tie-broken alphabetically", () => {
    // AAPL and AAPI are both ticker-prefix matches (same length) -- alphabetical
    // tie-break, same as searchCompanyDirectory's SQL ORDER BY.
    expect(rankCompanyMatches(directory, "aap").map((c) => c.ticker)).toEqual(["AAPI", "AAPL"]);
  });

  it("matches on company name prefix too, case-insensitively", () => {
    expect(rankCompanyMatches(directory, "micron").map((c) => c.ticker)).toEqual(["MU"]);
  });

  it("returns nothing for a blank query and respects the limit", () => {
    expect(rankCompanyMatches(directory, "   ")).toEqual([]);
    expect(rankCompanyMatches(directory, "a", 1)).toHaveLength(1);
  });
});
