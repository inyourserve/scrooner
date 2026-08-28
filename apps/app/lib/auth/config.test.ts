import { describe, expect, it } from "vitest";
import { getAuthEnvironmentStatus } from "./config";

describe("getAuthEnvironmentStatus", () => {
  it("requires a public URL and publishable key", () => {
    expect(getAuthEnvironmentStatus({})).toEqual({
      enabled: false,
      missing: [
        "NEXT_PUBLIC_SUPABASE_URL",
        "NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY",
      ],
      cookieDomain: null,
    });
  });

  it("enables auth only when both public values are present", () => {
    expect(
      getAuthEnvironmentStatus({
        NEXT_PUBLIC_SUPABASE_URL: "https://project.supabase.co",
        NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY: "sb_publishable_example",
        SUPABASE_AUTH_COOKIE_DOMAIN: " .scrooner.com ",
      }),
    ).toEqual({
      enabled: true,
      missing: [],
      cookieDomain: ".scrooner.com",
    });
  });

  it("never treats a service-role credential as browser configuration", () => {
    expect(
      getAuthEnvironmentStatus({
        SUPABASE_URL: "https://project.supabase.co",
        SUPABASE_SERVICE_ROLE_KEY: "must-stay-on-the-backend",
      }).enabled,
    ).toBe(false);
  });
});
