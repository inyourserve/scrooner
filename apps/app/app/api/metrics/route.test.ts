import { afterEach, describe, expect, it, vi } from "vitest";
import { GET, revalidate } from "./route";

vi.mock("@/lib/auth/require-user", () => ({ requireApiUser: vi.fn().mockResolvedValue(null) }));

describe("metrics catalog route", () => {
  afterEach(() => vi.unstubAllGlobals());

  it("shares the stable catalog through the authenticated browser cache", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      Response.json([{ metric: "roic" }]),
    );
    vi.stubGlobal("fetch", fetchMock);

    const response = await GET();

    expect(revalidate).toBe(3600);
    expect(fetchMock).toHaveBeenCalledWith(
      "http://127.0.0.1:8000/v1/metrics",
      expect.objectContaining({ next: { revalidate: 3600 } }),
    );
    expect(response.headers.get("cache-control")).toBe("private, max-age=300");
    await expect(response.json()).resolves.toEqual([{ metric: "roic" }]);
  });
});
