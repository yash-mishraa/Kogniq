import type { IDocumentService, ProcessDocumentParams } from "../interfaces/IDocumentService";
import type { DocumentItem, DocumentStatus, SemanticDocument } from "@/app/workspace/environments/documents/DocumentsTypes";
import { apiClient } from "@/lib/api/client";
import { ENDPOINTS } from "@/lib/api/endpoints";
import { REQUEST_POLICIES } from "@/lib/api/policies";

export class LiveDocumentService implements IDocumentService {
  async getDocuments(signal?: AbortSignal): Promise<DocumentItem[]> {
    const response = await apiClient.get<DocumentItem[]>("/api/v1/documents", {
      signal,
      ...REQUEST_POLICIES.retrieval
    });
    return response.data;
  }

  async getDocument(id: string, signal?: AbortSignal): Promise<DocumentItem> {
    const response = await apiClient.get<DocumentItem>("/api/v1/documents/" + id, {
      signal,
      ...REQUEST_POLICIES.retrieval
    });
    const doc = response.data;
    try {
        const semanticsResponse = await apiClient.get<SemanticDocument>("/api/v1/documents/" + id + "/semantics", { signal });
        doc.semantics = semanticsResponse.data;
    } catch (e) {
        console.error("Failed to fetch semantics", e);
    }
    return doc;
  }

  async processDocument(params: ProcessDocumentParams): Promise<DocumentItem> {
    const formData = new FormData();
    formData.append("file", params.file);
    
    const response = await apiClient.post<{ document_id: string; title: string; source: string; status: string }>(ENDPOINTS.documents.process, formData, {
      signal: params.signal,
      headers: {
        "Content-Type": undefined as unknown as string,
      },
      ...REQUEST_POLICIES.documentUpload
    });
    
    let frontendStatus: DocumentStatus = "Ready";
    if (response.data.status === "queued") frontendStatus = "Uploaded";
    if (response.data.status === "processing") frontendStatus = "Extracting";
    if (response.data.status === "completed") frontendStatus = "Ready";
    if (response.data.status === "failed") frontendStatus = "Failed";

    return {
      id: response.data.document_id,
      title: response.data.title,
      source: response.data.source,
      status: frontendStatus,
      importDate: new Date().toISOString()
    };
  }

  async deleteDocument(documentId: string): Promise<void> {
    await apiClient.delete(ENDPOINTS.documents.delete(documentId));
  }
}
