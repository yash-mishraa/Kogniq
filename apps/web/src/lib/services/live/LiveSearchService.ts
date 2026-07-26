import type { ISearchService, SearchQueryParams } from "../interfaces/ISearchService";
import type { SearchFinding } from "@/app/workspace/environments/search/SearchTypes";
import { apiClient } from "@/lib/api/client";
import { ENDPOINTS } from "@/lib/api/endpoints";
import { REQUEST_POLICIES } from "@/lib/api/policies";

interface RetrievalResultItem {
  chunk_id: string;
  similarity_score: number;
  chunk_text: string;
  chunk_index: number;
  metadata?: Record<string, string | number | boolean>;
  document_id?: string;
}

interface RetrievalResponse {
  results: RetrievalResultItem[];
}

export class LiveSearchService implements ISearchService {
  async search(params: SearchQueryParams): Promise<SearchFinding[]> {
    const response = await apiClient.post<RetrievalResponse>(
      ENDPOINTS.retrieval.search,
      { 
        query: params.query, 
        document_id: params.filter && params.filter !== "all" ? params.filter : undefined 
      },
      {
        signal: params.signal,
        ...REQUEST_POLICIES.search
      }
    );
    
    if (!response.data || !response.data.results) {
      return [];
    }

    return response.data.results.map((r: RetrievalResultItem) => {
      // Don't format the display strings here. Let the UI handle it.
      const docTitle = r.metadata?.title as string || "Unknown Document";
      const sectionTitle = r.metadata?.section_title as string | undefined;
      const pageNumber = r.metadata?.page_number as number | undefined;

      return {
        id: r.chunk_id,
        title: docTitle,
        documentId: r.document_id || "unknown",
        relevanceExplanation: `Similarity Score: ${(r.similarity_score * 100).toFixed(1)}%`,
        evidence: {
          snippet: r.chunk_text || "",
          location: pageNumber ? `Page ${pageNumber}` : `Index ${r.chunk_index}`,
          sectionTitle: sectionTitle
        },
        relatedConcepts: []
      };
    });
  }
}
