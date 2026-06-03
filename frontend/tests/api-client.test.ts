import { describe, expect, it, vi, afterEach } from "vitest";
import { ApiError, api } from "@/lib/api/client";

describe("api client", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("health returns status", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => ({ status: "ok", app_name: "RAGOps Platform" }),
      }),
    );
    const result = await api.health();
    expect(result.status).toBe("ok");
  });

  it("throws ApiError on failure", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 503,
        json: async () => ({
          error: { code: "embedding_unavailable", message: "Unavailable" },
        }),
      }),
    );
    await expect(api.health()).rejects.toThrow(ApiError);
  });
});
