import { afterEach, describe, expect, it, vi } from "vitest";
import { savedScreensApi } from "./client";

afterEach(() => vi.unstubAllGlobals());

describe("savedScreensApi", () => {
  it("forwards a user bearer token when listing screens", async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response("[]", { status: 200, headers: { "content-type": "application/json" } }));
    vi.stubGlobal("fetch", fetchMock);
    await savedScreensApi.list(async () => "user-token");
    expect(fetchMock).toHaveBeenCalledWith("/api/screens", expect.objectContaining({ headers: expect.objectContaining({ authorization: "Bearer user-token" }) }));
  });

  it("falls back to the same-origin authenticated cookie when the browser token snapshot is empty", async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response("[]", { status: 200, headers: { "content-type": "application/json" } }));
    vi.stubGlobal("fetch", fetchMock);
    await savedScreensApi.list(async () => null);
    expect(fetchMock).toHaveBeenCalledWith("/api/screens", expect.objectContaining({ headers: expect.not.objectContaining({ authorization: expect.anything() }) }));
  });
});
