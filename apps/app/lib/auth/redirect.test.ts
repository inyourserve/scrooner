import { describe, expect, it } from "vitest";
import { buildLoginHref, getSafeRedirectPath } from "./redirect";

const options = {
  allowedOrigins: ["https://app.scrooner.com", "http://localhost:3000"],
};

describe("getSafeRedirectPath", () => {
  it("keeps local application paths", () => {
    expect(getSafeRedirectPath("/screens/42/edit?from=screener#name", options)).toBe(
      "/screens/42/edit?from=screener#name",
    );
  });

  it("converts an allowed absolute URL to a local path", () => {
    expect(
      getSafeRedirectPath(
        "https://app.scrooner.com/watchlist?add=AAPL",
        options,
      ),
    ).toBe("/watchlist?add=AAPL");
  });

  it.each([
    "https://evil.example/collect",
    "//evil.example/collect",
    "/\\evil.example/collect",
    "https://user:password@app.scrooner.com/account",
    "/screener%0d%0aSet-Cookie:bad=1",
  ])("rejects unsafe destination %s", (destination) => {
    expect(getSafeRedirectPath(destination, options)).toBe("/screener");
  });

  it("supports an explicit safe fallback", () => {
    expect(getSafeRedirectPath(null, { fallback: "/" })).toBe("/");
  });
});

describe("buildLoginHref", () => {
  it("encodes the validated redirect path", () => {
    expect(buildLoginHref("/screens?sort=recent", options)).toBe(
      "/login?redirect_url=%2Fscreens%3Fsort%3Drecent",
    );
  });
});
