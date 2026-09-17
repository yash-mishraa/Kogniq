import type { IStudyService, GenerateStudyParams } from "../interfaces/IStudyService";
import type { StudyMaterial, StudyConcept } from "@/app/workspace/environments/study/StudyTypes";
import { apiClient } from "@/lib/api/client";

interface LearningMaterials {
  explanation?: { body: string };
  summary?: { body: string };
  notes?: { body: string };
  flashcards?: { body: Array<{ question: string; answer: string }> };
  quiz?: {
    body: Array<{
      question: string;
      options: Array<{ id: string; text: string }>;
      correct_answer: string;
      explanation: string;
    }>;
  };
}

export class LiveStudyService implements IStudyService {
  async generateMaterial(params: GenerateStudyParams): Promise<StudyMaterial> {
    const documentId = params.topicId; // topicId corresponds to documentId

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
        return this.mapToStudyMaterial(documentId, data.materials);
      }

      // Wait 3 seconds before polling again
      await new Promise((resolve) => setTimeout(resolve, 3000));
    }
  }

  private mapToStudyMaterial(documentId: string, materials: LearningMaterials): StudyMaterial {
    const fallbackConcept: StudyConcept = {
      id: documentId,
      title: "Learning Material",
      sourceDocument: "Document",
      relatedConcepts: [],
    };

    const understandStr = materials.explanation?.body || materials.summary?.body || "";
    const reviewStr = materials.notes?.body || "";
    const flashcardsArray = materials.flashcards?.body || [];
    const quizArray = materials.quiz?.body || [];

    const recall = flashcardsArray.map((f) => ({
      prompt: f.question,
      explanation: f.answer,
    }));

    const test = quizArray.map((q, i) => {
      const correctOptionIndex = q.options.findIndex((o) => o.id === q.correct_answer);
      return {
        id: "id" in q ? String(q.id) : `q${i}`,
        question: q.question,
        options: q.options,
        correctOptionIndex: correctOptionIndex >= 0 ? correctOptionIndex : 0,
        explanation: q.explanation,
      };
    });

    return {
      concept: fallbackConcept,
      understand: {
        intuition: "",
        whyItMatters: "",
        keyTakeaways: [],
        markdown: understandStr,
      },
      review: {
        notes: [],
        markdown: reviewStr,
      },
      recall,
      test,
    };
  }
}
