import { describe, it, expect, vi, beforeEach } from "vitest";
import { LiveResourceService } from "./LiveResourceService";
import { apiClient } from "@/lib/api/client";

vi.mock("@/lib/api/client", () => ({
  apiClient: {
    get: vi.fn(),
  },
}));

describe("LiveResourceService", () => {
  let service: LiveResourceService;

  beforeEach(() => {
    service = new LiveResourceService();
    vi.resetAllMocks();
  });

  it("should fetch resource list with pagination", async () => {
    const mockData = [{ id: "r1", title: "Test" }];
    vi.mocked(apiClient.get).mockResolvedValueOnce({ data: mockData, status: 200 });

    const result = await service.listResources(10, 20);
    
    expect(apiClient.get).toHaveBeenCalledWith("/api/v1/resources", expect.objectContaining({
      params: { limit: 10, offset: 20 },
    }));
    expect(result).toEqual(mockData);
  });

  it("should fetch resource details", async () => {
    const mockData = { id: "r1", title: "Test" };
    vi.mocked(apiClient.get).mockResolvedValueOnce({ data: mockData, status: 200 });

    const result = await service.getResource("r1");
    
    expect(apiClient.get).toHaveBeenCalledWith("/api/v1/resources/r1", expect.any(Object));
    expect(result).toEqual(mockData);
  });

  it("should fetch sections", async () => {
    const mockData = [{ id: "s1", title: "Sec 1" }];
    vi.mocked(apiClient.get).mockResolvedValueOnce({ data: mockData, status: 200 });

    const result = await service.getResourceSections("r1");
    
    expect(apiClient.get).toHaveBeenCalledWith("/api/v1/resources/r1/sections", expect.any(Object));
    expect(result).toEqual(mockData);
  });

  it("should fetch chunks", async () => {
    const mockData = [{ id: "c1", text: "Chunk 1" }];
    vi.mocked(apiClient.get).mockResolvedValueOnce({ data: mockData, status: 200 });

    const result = await service.getResourceChunks("r1", 50, 10);
    
    expect(apiClient.get).toHaveBeenCalledWith("/api/v1/resources/r1/chunks", expect.objectContaining({
      params: { limit: 50, offset: 10 }
    }));
    expect(result).toEqual(mockData);
  });

  it("should handle error responses correctly", async () => {
    vi.mocked(apiClient.get).mockRejectedValueOnce(new Error("Network Error"));
    await expect(service.listResources()).rejects.toThrow("Network Error");
  });
});
