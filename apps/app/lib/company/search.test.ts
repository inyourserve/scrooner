import { describe, expect, it } from "vitest";
import { addRecentCompany, normalizeCompanyQuery, normalizeRecentCompanies, type SearchCompany } from "./search";
const apple: SearchCompany = { ticker: "AAPL", company_name: "Apple Inc.", exchange: "Nasdaq", sector: "Technology" };
describe("company search", () => {
  it("normalizes and caps queries", () => { expect(normalizeCompanyQuery("  Apple   Inc.  ")).toBe("apple inc."); expect(normalizeCompanyQuery("x".repeat(80))).toHaveLength(64); });
  it("validates, deduplicates, and caps recent companies", () => { const result = normalizeRecentCompanies([apple, apple, ...["MSFT", "NVDA", "AMZN", "COST", "JPM"].map((ticker) => ({ ticker, company_name: ticker, exchange: null, sector: null }))]); expect(result.map((item) => item.ticker)).toEqual(["AAPL", "MSFT", "NVDA", "AMZN", "COST"]); });
  it("moves a selection to the front", () => { const msft = { ...apple, ticker: "MSFT", company_name: "Microsoft" }; expect(addRecentCompany([apple, msft], msft).map((item) => item.ticker)).toEqual(["MSFT", "AAPL"]); });
});
