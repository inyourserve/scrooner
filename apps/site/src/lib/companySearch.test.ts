import assert from "node:assert/strict";
import test from "node:test";

import {
  addRecentCompany,
  normalizeCompanyQuery,
  normalizeRecentCompanies,
  type SearchCompany,
} from "./companySearch.ts";

const apple: SearchCompany = {
  ticker: "AAPL",
  company_name: "Apple Inc.",
  exchange: "Nasdaq",
  sector: "Technology",
};

test("normalizes a company query before it reaches the public endpoint", () => {
  assert.equal(normalizeCompanyQuery("  Apple   Inc.  "), "apple inc.");
  assert.equal(normalizeCompanyQuery("x".repeat(80)).length, 64);
});

test("recent companies are validated, deduplicated, and capped", () => {
  const recent = normalizeRecentCompanies([
    apple,
    { ...apple, company_name: "Duplicate" },
    { ticker: "MSFT", company_name: "Microsoft", exchange: null, sector: null },
    { ticker: "NVDA", company_name: "Nvidia", exchange: null, sector: null },
    { ticker: "AMZN", company_name: "Amazon", exchange: null, sector: null },
    { ticker: "COST", company_name: "Costco", exchange: null, sector: null },
    { ticker: "JPM", company_name: "JPMorgan", exchange: null, sector: null },
    { ticker: 42, company_name: "Invalid", exchange: null, sector: null },
  ]);

  assert.deepEqual(recent.map((company) => company.ticker), ["AAPL", "MSFT", "NVDA", "AMZN", "COST"]);
});

test("a selection moves to the front of recent companies", () => {
  const microsoft: SearchCompany = {
    ticker: "MSFT",
    company_name: "Microsoft Corp.",
    exchange: "Nasdaq",
    sector: "Technology",
  };
  const next = addRecentCompany([apple, microsoft], microsoft);
  assert.deepEqual(next.map((company) => company.ticker), ["MSFT", "AAPL"]);
});
