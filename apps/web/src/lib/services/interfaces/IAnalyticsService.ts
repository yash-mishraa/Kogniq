export interface EventBatchItem {
  event_id: string;
  event_type: string;
  resource_id: string;
  data: Record<string, unknown>;
  section_id?: string | null;
  chunk_id?: string | null;
  idempotency_key?: string | null;
}

export interface ResourceProgress {
  resource_opened: boolean;
  total_sections: number;
  total_chunks: number;
  viewed_sections: number;
  viewed_chunks: number;
  last_activity: string | null;
}

export interface AnalyticsMetrics {
  quizzes_completed: number;
  average_quiz_accuracy: number;
  flashcards_reviewed: number;
}

export interface IAnalyticsService {
  recordEventsBatch(events: EventBatchItem[], options?: { signal?: AbortSignal, keepalive?: boolean }): Promise<void>;
  enqueueBatchEvent(event: EventBatchItem): void;
  initializeDeliveryQueue(sessionUserId: string | null): void;
  getResourceProgress(resourceId: string, signal?: AbortSignal): Promise<ResourceProgress>;
  getMetrics(timeRange: "7d" | "30d" | "all", options?: { documentId?: string, signal?: AbortSignal }): Promise<AnalyticsMetrics>;
}
