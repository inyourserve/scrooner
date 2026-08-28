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

  it("requires a user session before making a request", async () => {
    const fetchMock = vi.fn(); vi.stubGlobal("fetch", fetchMock);
    await expect(savedScreensApi.list(async () => null)).rejects.toThrow("Sign in");
    expect(fetchMock).not.toHaveBeenCalled();
  });
});
