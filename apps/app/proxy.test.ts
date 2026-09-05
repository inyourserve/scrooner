import { describe, expect, it } from "vitest";
import { config } from "./proxy";

describe("auth proxy scope", () => {
  it("protects every screening page and endpoint", () => {
    expect(config.matcher).toEqual([
      "/",
      "/screener/:path*",
      "/saved-screens/:path*",
      "/account/:path*",
      "/api/ask/:path*",
      "/api/screen/:path*",
      "/api/screens/:path*",
      "/api/metrics/:path*",
    ]);
  });

  it("does not include the former global catch-all", () => {
    expect(config.matcher).not.toContain(
      "/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)",
    );
  });
});
