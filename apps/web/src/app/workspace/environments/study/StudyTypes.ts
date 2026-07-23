export type LearningMode = "understand" | "reflection" | "review" | "recall" | "test";

export interface StudyConcept {
  id: string;
  title: string;
  sourceDocument: string;
  relatedConcepts: string[];
}

export interface UnderstandContent {
  intuition: string;
  whyItMatters: string;
  keyTakeaways: string[];
}

export interface ReviewContent {
  notes: { section: string; points: string[] }[];
}

export interface RecallContent {
  prompt: string;
  explanation: string;
}

export interface TestContent {
  question: string;
  options: string[];
  correctOptionIndex: number;
  explanation: string;
}

export interface StudyMaterial {
  concept: StudyConcept;
  understand: UnderstandContent;
  review: ReviewContent;
  recall: RecallContent[];
  test: TestContent[];
}

export interface StudyState {
  isStudying: boolean;
  activeMode: LearningMode;
  material: StudyMaterial | null;
  recallIndex: number;
  testIndex: number;
}

export type StudyAction =
  | { type: "START_STUDY"; payload: StudyMaterial }
  | { type: "SET_MODE"; payload: LearningMode }
  | { type: "NEXT_RECALL" }
  | { type: "NEXT_TEST" }
  | { type: "END_STUDY" };
