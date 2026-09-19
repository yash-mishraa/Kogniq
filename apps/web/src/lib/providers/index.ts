import type { IAuthService } from "../services/interfaces/IAuthService";
import type { IDocumentService } from "../services/interfaces/IDocumentService";
import type { IKnowledgeService } from "../services/interfaces/IKnowledgeService";
import type { INotebookService } from "../services/interfaces/INotebookService";
import type { ISearchService } from "../services/interfaces/ISearchService";
import type { IStudyService } from "../services/interfaces/IStudyService";
import type { IFlashcardsService } from "../services/interfaces/IFlashcardsService";
import type { IQuizService } from "../services/interfaces/IQuizService";
import type { IResourceService } from "../services/interfaces/IResourceService";

import { MockAuthService } from "../services/mock/MockAuthService";
import { MockDocumentService } from "../services/mock/MockDocumentService";
import { MockQuizService } from "../services/mock/MockQuizService";
import { MockFlashcardsService } from "../services/mock/MockFlashcardsService";
import { MockResourceService } from "../services/mock/MockResourceService";

import { LiveAuthService } from "../services/live/LiveAuthService";
import { LiveDocumentService } from "../services/live/LiveDocumentService";
import { LiveKnowledgeService } from "../services/live/LiveKnowledgeService";
import { LiveNotebookService } from "../services/live/LiveNotebookService";
import { LiveSearchService } from "../services/live/LiveSearchService";
import { LiveStudyService } from "../services/live/LiveStudyService";
import { LiveFlashcardsService } from "../services/live/LiveFlashcardsService";
import { LiveQuizService } from "../services/live/LiveQuizService";
import { LiveAnalyticsService } from "../services/live/LiveAnalyticsService";
import { LiveResourceService } from "../services/live/LiveResourceService";
import type { IAnalyticsService } from "../services/interfaces/IAnalyticsService";

export type ProviderMode = "mock" | "live";

export interface IServiceProvider {
  auth: IAuthService;
  documents: IDocumentService;
  knowledge: IKnowledgeService;
  notebooks: INotebookService;
  search: ISearchService;
  study: IStudyService;
  flashcards: IFlashcardsService;
  quiz: IQuizService;
  analytics: IAnalyticsService;
  resources: IResourceService;
}

class ServiceProviderFactory {
  private activeMode: ProviderMode = (process.env.NEXT_PUBLIC_PROVIDER_MODE as ProviderMode) || "mock";
  
  private mockProvider: IServiceProvider = {
    auth: new MockAuthService(),
    documents: new MockDocumentService(),
    knowledge: new LiveKnowledgeService(),
    notebooks: new LiveNotebookService(),
    search: new LiveSearchService(),
    study: new LiveStudyService(),
    flashcards: new MockFlashcardsService(),
    quiz: new MockQuizService(),
    analytics: new LiveAnalyticsService(),
    resources: new MockResourceService(),
  };

  private liveProvider: IServiceProvider = {
    auth: new LiveAuthService(),
    documents: new LiveDocumentService(),
    knowledge: new LiveKnowledgeService(),
    notebooks: new LiveNotebookService(),
    search: new LiveSearchService(),
    study: new LiveStudyService(),
    flashcards: new LiveFlashcardsService(),
    quiz: new LiveQuizService(),
    analytics: new LiveAnalyticsService(),
    resources: new LiveResourceService(),
  };

  getProvider(): IServiceProvider {
    return this.activeMode === "live" ? this.liveProvider : this.mockProvider;
  }

  setMode(mode: ProviderMode) {
    this.activeMode = mode;
  }
}

export const serviceProvider = new ServiceProviderFactory();
