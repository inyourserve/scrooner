import { describe, expect, it } from "vitest";
import { applySuggestion, getSuggestions, type NlVocabulary } from "./suggest";

const vocabulary: NlVocabulary = {
  metrics: [
    { phrase: "return on equity", metric_names: ["roe"] },
    { phrase: "return on invested capital", metric_names: ["roic"] },
    { phrase: "revenue growth yoy", metric_names: ["revenue_growth_yoy"] },
    { phrase: "revenue growth", metric_names: ["revenue_growth_yoy", "revenue_growth_3y_cagr"] },
  ],
  operators: [
    { phrase: "above", operator: ">" },
    { phrase: "at least", operator: ">=" },
  ],
  sectors: [{ phrase: "technology companies", field: "sector", value: "Technology" }],
};

describe("getSuggestions", () => {
  it("matches the whole-clause prefix for the first word of a query (\"re\")", () => {
    const suggestions = getSuggestions(vocabulary, "re", 2);
    const phrases = suggestions.map((s) => s.phrase);
    expect(phrases).toContain("return on equity");
    expect(phrases).toContain("return on invested capital");
    expect(phrases).toContain("revenue growth yoy");
    expect(phrases).toContain("revenue growth");
  });

  it("matches an operator by the last word typed after an earlier word (\"roe ab\")", () => {
    const text = "roe ab";
    const suggestions = getSuggestions(vocabulary, text, text.length);
    expect(suggestions.map((s) => s.phrase)).toEqual(["above"]);
    // Replacement range must cover only "ab", not "roe ab" -- the earlier
    // word must survive the insertion.
    expect(suggestions[0].replaceStart).toBe(4);
    expect(suggestions[0].replaceEnd).toBe(6);
  });

  it("resets the clause boundary after a literal \"and\"", () => {
    const text = "roe above 30% and re";
    const suggestions = getSuggestions(vocabulary, text, text.length);
    expect(suggestions.map((s) => s.phrase)).toContain("return on equity");
    expect(suggestions[0].replaceStart).toBe(text.indexOf("re", text.indexOf("and")));
  });

  it("requires at least 2 characters before suggesting anything", () => {
    expect(getSuggestions(vocabulary, "r", 1)).toEqual([]);
    expect(getSuggestions(vocabulary, "", 0)).toEqual([]);
  });

  it("is case-insensitive", () => {
    expect(getSuggestions(vocabulary, "RE", 2).map((s) => s.phrase)).toContain("return on equity");
  });

  it("matches sector phrases the same way", () => {
    expect(getSuggestions(vocabulary, "tech", 4).map((s) => s.phrase)).toContain("technology companies");
  });

  it("caps the result and ranks shorter phrases first within a tier", () => {
    const suggestions = getSuggestions(vocabulary, "re", 2);
    expect(suggestions.length).toBeLessThanOrEqual(8);
    expect(suggestions[0].phrase.length).toBeLessThanOrEqual(suggestions[suggestions.length - 1].phrase.length);
  });

  it("returns nothing for a prefix that matches no known phrase", () => {
    expect(getSuggestions(vocabulary, "xyzzy", 5)).toEqual([]);
  });
});

describe("applySuggestion", () => {
  it("replaces only the matched extent and leaves earlier words intact", () => {
    const text = "roe ab";
    const suggestions = getSuggestions(vocabulary, text, text.length);
    const result = applySuggestion(text, suggestions[0]);
    expect(result.text).toBe("roe above ");
    expect(result.cursor).toBe(result.text.length);
  });

  it("replaces the whole first-word prefix for a fresh clause", () => {
    const result = applySuggestion("re", { phrase: "return on equity", kind: "metric", replaceStart: 0, replaceEnd: 2 });
    expect(result.text).toBe("return on equity ");
  });
});
