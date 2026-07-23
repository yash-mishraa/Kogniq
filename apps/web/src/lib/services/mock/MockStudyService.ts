import type { IStudyService, GenerateStudyParams } from "../interfaces/IStudyService";
import type { StudyMaterial } from "@/app/workspace/environments/study/StudyTypes";
import { MOCK_STUDY_MATERIAL } from "@/app/workspace/environments/study/StudyState";

export class MockStudyService implements IStudyService {
  async generateMaterial(params: GenerateStudyParams): Promise<StudyMaterial> {
    return new Promise((resolve, reject) => {
      const timeout = setTimeout(() => {
        resolve(MOCK_STUDY_MATERIAL);
      }, 1500);

      if (params.signal) {
        params.signal.addEventListener("abort", () => {
          clearTimeout(timeout);
          reject(new DOMException("Aborted", "AbortError"));
        });
      }
    });
  }
}
