import type { IFlashcardsService, GetFlashcardsParams, FlashcardData } from "../interfaces/IFlashcardsService";
import { apiClient } from "@/lib/api/client";

interface LearningMaterials {
  flashcards?: { body: Array<{ question: string; answer: string; difficulty?: string; id?: string }> };
}

export class LiveFlashcardsService implements IFlashcardsService {
  async getFlashcards(params: GetFlashcardsParams): Promise<FlashcardData[]> {
    const documentId = params.documentId;

    while (true) {
      if (params.signal?.aborted) {
        throw new Error("Aborted");
      }

      const response = await apiClient.get<{ status: string; materials: LearningMaterials | null }>(
        `/api/v1/learning/${documentId}`,
        { signal: params.signal }
      );

      const data = response.data;
      if (data.status === "failed" || data.status === "error") {
        throw new Error("Failed to generate learning material");
      }
      if (data.status === "completed" || data.status === "COMPLETED_WITH_WARNINGS" || (data.status === "COMPLETED" && data.materials)) {
        if (!data.materials) {
           throw new Error("Materials were empty but status was completed");
        }
        return this.mapToFlashcards(data.materials);
      }

      // Wait 3 seconds before polling again
      await new Promise((resolve) => setTimeout(resolve, 3000));
    }
  }

  private mapToFlashcards(materials: LearningMaterials): FlashcardData[] {
    const flashcardsArray = materials.flashcards?.body || [];
    return flashcardsArray.map((f, i) => ({
      id: f.id || `flashcard-${i}`,
      question: f.question,
      answer: f.answer,
      difficulty: f.difficulty || "medium",
    }));
  }
}
