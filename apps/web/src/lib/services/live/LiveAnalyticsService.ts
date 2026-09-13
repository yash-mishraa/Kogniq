export interface AnalyticsEvent {
  event_id: string;
  event_type: "quiz_completed" | "flashcard_reviewed";
  document_id: string;
  data: Record<string, unknown>;
}

export interface AnalyticsMetrics {
  quizzes_completed: number;
  average_quiz_accuracy: number;
  flashcards_reviewed: number;
}

export class LiveAnalyticsService {
  async recordEvent(event: AnalyticsEvent): Promise<void> {
    const response = await fetch("/api/v1/analytics/events", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(event),
    });
    
    if (!response.ok) {
      throw new Error(`Failed to record analytics event: ${response.statusText}`);
    }
  }

  async getMetrics(timeRange: "7d" | "30d" | "all", signal?: AbortSignal): Promise<AnalyticsMetrics> {
    const response = await fetch(`/api/v1/analytics?time_range=${timeRange}`, {
      signal
    });
    
    if (!response.ok) {
      throw new Error(`Failed to fetch analytics metrics: ${response.statusText}`);
    }
    
    return await response.json();
  }
}
