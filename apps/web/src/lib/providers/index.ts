import type { IAuthService } from "../services/interfaces/IAuthService";
import type { IDocumentService } from "../services/interfaces/IDocumentService";
import type { IKnowledgeService } from "../services/interfaces/IKnowledgeService";
import type { INotebookService } from "../services/interfaces/INotebookService";
import type { ISearchService } from "../services/interfaces/ISearchService";
import type { IStudyService } from "../services/interfaces/IStudyService";

import { MockAuthService } from "../services/mock/MockAuthService";
import { MockDocumentService } from "../services/mock/MockDocumentService";
import { MockKnowledgeService } from "../services/mock/MockKnowledgeService";
import { MockNotebookService } from "../services/mock/MockNotebookService";
import { MockSearchService } from "../services/mock/MockSearchService";
import { MockStudyService } from "../services/mock/MockStudyService";

import { LiveAuthService } from "../services/live/LiveAuthService";
import { LiveDocumentService } from "../services/live/LiveDocumentService";
import { LiveKnowledgeService } from "../services/live/LiveKnowledgeService";
import { LiveNotebookService } from "../services/live/LiveNotebookService";
import { LiveSearchService } from "../services/live/LiveSearchService";
import { LiveStudyService } from "../services/live/LiveStudyService";

export type ProviderMode = "mock" | "live";

export interface IServiceProvider {
  auth: IAuthService;
  documents: IDocumentService;
  knowledge: IKnowledgeService;
  notebooks: INotebookService;
  search: ISearchService;
  study: IStudyService;
}

class ServiceProviderFactory {
  private activeMode: ProviderMode = (process.env.NEXT_PUBLIC_PROVIDER_MODE as ProviderMode) || "mock";
  
  private mockProvider: IServiceProvider = {
    auth: new MockAuthService(),
    documents: new MockDocumentService(),
    knowledge: new MockKnowledgeService(),
    notebooks: new MockNotebookService(),
    search: new MockSearchService(),
    study: new MockStudyService(),
  };

  private liveProvider: IServiceProvider = {
    auth: new LiveAuthService(),
    documents: new LiveDocumentService(),
    knowledge: new LiveKnowledgeService(),
    notebooks: new LiveNotebookService(),
    search: new LiveSearchService(),
    study: new LiveStudyService(),
  };

  getProvider(): IServiceProvider {
    return this.activeMode === "live" ? this.liveProvider : this.mockProvider;
  }

  setMode(mode: ProviderMode) {
    this.activeMode = mode;
  }
}

export const serviceProvider = new ServiceProviderFactory();
