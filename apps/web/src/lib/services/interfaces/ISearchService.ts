import type { SearchFinding } from "@/app/workspace/environments/search/SearchTypes";

export interface SearchQueryParams {
  query: string;
  filter?: string;
  signal?: AbortSignal;
}

export interface ISearchService {
  search(params: SearchQueryParams): Promise<SearchFinding[]>;
}
