import { afterEach, describe, expect, it, vi } from "vitest";
import { GET, revalidate } from "./route";

describe("metrics catalog route", () => {
  afterEach(() => vi.unstubAllGlobals());

  it("shares the stable catalog through the Next and CDN caches", async () => {
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
    expect(response.headers.get("cache-control")).toBe(
      "public, s-maxage=3600, stale-while-revalidate=86400",
    );
    await expect(response.json()).resolves.toEqual([{ metric: "roic" }]);
  });
});
