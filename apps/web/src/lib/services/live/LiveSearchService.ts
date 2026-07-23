import type { ISearchService, SearchQueryParams } from "../interfaces/ISearchService";
import type { SearchFinding } from "@/app/workspace/environments/search/SearchTypes";
import { apiClient } from "@/lib/api/client";
import { ENDPOINTS } from "@/lib/api/endpoints";
import { REQUEST_POLICIES } from "@/lib/api/policies";

export class LiveSearchService implements ISearchService {
  async search(params: SearchQueryParams): Promise<SearchFinding[]> {
    const response = await apiClient.post<SearchFinding[]>(
      ENDPOINTS.retrieval.search,
      { query: params.query, filter: params.filter },
      {
        signal: params.signal,
        ...REQUEST_POLICIES.search
      }
    );
    return response.data;
  }
}
