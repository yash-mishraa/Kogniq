import type { EnvironmentId, EnvironmentMetadata } from "../WorkspaceTypes";
import { analyticsEnvironment } from "./analytics";
import { documentsEnvironment } from "./documents";
import { flashcardsEnvironment } from "./flashcards";
import { graphEnvironment } from "./graph";
import { knowledgeEnvironment } from "./knowledge";
import { quizEnvironment } from "./quiz";
import { searchEnvironment } from "./search";
import { studioEnvironment } from "./studio";
import { studyEnvironment } from "./study";

export class EnvironmentRegistry {
  private readonly entries = new Map<EnvironmentId, EnvironmentMetadata>();

  constructor(initial: readonly EnvironmentMetadata[] = []) { initial.forEach((environment) => this.registerEnvironment(environment)); }
  registerEnvironment(environment: EnvironmentMetadata) { this.entries.set(environment.id, environment); }
  getEnvironment(id: EnvironmentId) { return this.entries.get(id); }
  listEnvironments() { return [...this.entries.values()]; }
}

export const environmentRegistry = new EnvironmentRegistry([documentsEnvironment, graphEnvironment, knowledgeEnvironment, searchEnvironment, studioEnvironment, studyEnvironment, flashcardsEnvironment, quizEnvironment, analyticsEnvironment]);
export const environments = environmentRegistry.listEnvironments();
