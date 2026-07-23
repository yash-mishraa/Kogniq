import type { StudyMaterial } from "@/app/workspace/environments/study/StudyTypes";

export interface GenerateStudyParams {
  topicId: string;
  signal?: AbortSignal;
}

export interface IStudyService {
  generateMaterial(params: GenerateStudyParams): Promise<StudyMaterial>;
}
