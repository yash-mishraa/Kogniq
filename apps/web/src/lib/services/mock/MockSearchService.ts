import type { ISearchService, SearchQueryParams } from "../interfaces/ISearchService";
import type { SearchFinding } from "@/app/workspace/environments/search/SearchTypes";
import { MOCK_FINDINGS } from "@/app/workspace/environments/search/SearchState";

export class MockSearchService implements ISearchService {
  async search(params: SearchQueryParams): Promise<SearchFinding[]> {
    return new Promise((resolve, reject) => {
      // Simulate network delay
      const timeout = setTimeout(() => {
        const query = params.query.toLowerCase();
        
        if (query.includes("error")) {
          return reject(new Error("Simulated mock search error"));
        }
        
        let results: SearchFinding[] = [];
        if (query.includes("attention") || query.includes("transformer")) {
          results = MOCK_FINDINGS["self attention"];
        } else if (query.includes("database") || query.includes("sql")) {
          results = MOCK_FINDINGS["database"];
        } else if (query === "") {
          results = [];
        } else {
          // generic match
          results = MOCK_FINDINGS["self attention"];
        }
        
        resolve(results || []);
      }, 1000);

      // Handle cancellation
      if (params.signal) {
        params.signal.addEventListener("abort", () => {
          clearTimeout(timeout);
          reject(new DOMException("Aborted", "AbortError"));
        });
      }
    });
  }
}
