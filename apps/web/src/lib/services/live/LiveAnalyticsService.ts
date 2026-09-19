import { AnalyticsDeliveryQueue } from "./AnalyticsDeliveryQueue";

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

export class LiveAnalyticsService {
  private queue: AnalyticsDeliveryQueue;

  constructor() {
    this.queue = new AnalyticsDeliveryQueue(this.recordEventsBatch.bind(this));
  }

  enqueueBatchEvent(event: EventBatchItem): void {
    this.queue.enqueueEvent(event);
  }

  initializeDeliveryQueue(sessionUserId: string | null): void {
    this.queue.initialize(sessionUserId);
  }

  async recordEventsBatch(events: EventBatchItem[], options?: { signal?: AbortSignal, keepalive?: boolean }): Promise<void> {
    const response = await fetch("/api/v1/analytics/events/batch", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ events }),
      signal: options?.signal,
      keepalive: options?.keepalive
    });
    
    if (!response.ok) {
      throw new Error(`Failed to record batch analytics events: ${response.status} ${response.statusText}`);
    }
  }

  async getResourceProgress(resourceId: string, signal?: AbortSignal): Promise<ResourceProgress> {
    const response = await fetch(`/api/v1/analytics/progress/${resourceId}`, {
      signal
    });
    
    if (!response.ok) {
      throw new Error(`Failed to fetch resource progress: ${response.statusText}`);
    }
    
    return await response.json();
  }

  async getMetrics(timeRange: "7d" | "30d" | "all", options?: { documentId?: string, signal?: AbortSignal }): Promise<AnalyticsMetrics> {
    const url = options?.documentId 
      ? `/api/v1/analytics?time_range=${timeRange}&document_id=${options.documentId}`
      : `/api/v1/analytics?time_range=${timeRange}`;
    const response = await fetch(url, {
      signal: options?.signal
    });
    
    if (!response.ok) {
      throw new Error(`Failed to fetch analytics metrics: ${response.statusText}`);
    }
    
    return await response.json();
  }
}
