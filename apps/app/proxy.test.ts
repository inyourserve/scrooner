import { describe, expect, it } from "vitest";
import { config } from "./proxy";

describe("auth proxy scope", () => {
  it("limits session refresh to authenticated journeys", () => {
    expect(config.matcher).toEqual([
      "/account/:path*",
      "/saved-screens/:path*",
      "/api/screens/:path*",
    ]);
  });

  it("does not include the former global catch-all", () => {
    expect(config.matcher).not.toContain(
      "/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)",
    );
  });
});
