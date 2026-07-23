import type { IDocumentService, ProcessDocumentParams } from "../interfaces/IDocumentService";
import type { DocumentItem } from "@/app/workspace/environments/documents/DocumentsTypes";
import { apiClient } from "@/lib/api/client";
import { ENDPOINTS } from "@/lib/api/endpoints";
import { REQUEST_POLICIES } from "@/lib/api/policies";

export class LiveDocumentService implements IDocumentService {
  async getDocuments(signal?: AbortSignal): Promise<DocumentItem[]> {
    // We assume backend returns something we map, but for now we just cast or return empty array if not implemented
    const response = await apiClient.get<DocumentItem[]>("/api/v1/documents", {
      signal,
      ...REQUEST_POLICIES.retrieval
    });
    return response.data;
  }

  async processDocument(params: ProcessDocumentParams): Promise<DocumentItem> {
    const formData = new FormData();
    formData.append("file", params.file);
    
    // Note: apiClient defaults to JSON, so for FormData we would need to let fetch handle it,
    // or just use fetch directly, or extend apiClient to handle FormData.
    // For now we will rely on apiClient post but override headers to let browser set boundary.
    const response = await apiClient.post<DocumentItem>(ENDPOINTS.documents.process, formData, {
      signal: params.signal,
      headers: {
        // Remove Content-Type so browser can set multipart/form-data with boundary
        "Content-Type": undefined as unknown as string,
      },
      ...REQUEST_POLICIES.documentUpload
    });
    
    return response.data;
  }
}
