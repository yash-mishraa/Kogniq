/**
 * Typed client for the Kogniq RAG console.
 *
 * Everything is same-origin: Next.js rewrites `/api/*` to the FastAPI service,
 * so the HttpOnly session cookie is sent automatically and no token ever
 * reaches client-side JavaScript.
 */

const API_ROOT = "/api/v1";

export class ApiRequestError extends Error {
  readonly status: number;
  readonly code: string;

  constructor(message: string, status: number, code = "request_failed") {
    super(message);
    this.name = "ApiRequestError";
    this.status = status;
    this.code = code;
  }
}

type Json = Record<string, unknown>;

async function readError(response: Response): Promise<ApiRequestError> {
  let message = response.statusText || `Request failed with ${response.status}`;
  let code = "request_failed";
  try {
    const body = (await response.json()) as Json;
    const envelope = body.error as Json | undefined;
    if (envelope) {
      message = String(envelope.message ?? message);
      code = String(envelope.code ?? code);
    } else if (typeof body.detail === "string") {
      message = body.detail;
    } else if (Array.isArray(body.detail)) {
      message = body.detail
        .map((item) => {
          if (item && typeof item === "object" && "msg" in item) {
            return String((item as Json).msg);
          }
          return String(item);
        })
        .join("; ");
      code = "validation_error";
    }
  } catch {
    // Non-JSON error body: keep the status text.
  }
  return new ApiRequestError(message, response.status, code);
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  if (init.body && !(init.body instanceof FormData) && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  const response = await fetch(`${API_ROOT}${path}`, {
    credentials: "same-origin",
    ...init,
    headers,
  });
  if (!response.ok) {
    throw await readError(response);
  }
  if (response.status === 204) {
    return undefined as T;
  }
  return (await response.json()) as T;
}

function jsonBody(value: unknown): string {
  return JSON.stringify(value);
}

// ---------------------------------------------------------------------------
// Contracts
// ---------------------------------------------------------------------------

export interface SessionUser {
  id: string;
  email: string;
  display_name?: string;
}

export interface DocumentSummary {
  id: string;
  title: string;
  source: string;
  status: string;
  importDate: string;
  error?: string | null;
  chunk_count: number;
  embedding_model?: string | null;
  embedding_dimensions?: number | null;
  chunker_config?: string | null;
  indexed_at?: string | null;
  needs_reindex: boolean;
}

export interface DocumentDetail extends DocumentSummary {
  pages: {
    page_number: number;
    width?: number | null;
    height?: number | null;
    blocks: { id: string; text: string; type: string; order: number }[];
  }[];
}

export interface ChunkRecord {
  id: string;
  chunk_index: number;
  text: string;
  title?: string | null;
  page_number?: number | null;
  section_title?: string | null;
  section_id?: string | null;
  section_path?: string | null;
  created_at?: string | null;
  character_count: number;
  estimated_tokens: number;
}

export interface ChunkInspection {
  document_id: string;
  status: string;
  chunk_count: number;
  chunks: ChunkRecord[];
}

export interface Overview {
  generated_at: string;
  documents: {
    total: number;
    ready: number;
    processing: number;
    failed: number;
    unindexed: number;
    chunks: number;
  };
  index: {
    provider: string;
    collection: string;
    vector_count: number | null;
    indexed_documents: number;
    embedding_model: string;
    embedding_dimensions: number;
    chunker_config: string | null;
    metadata: Record<string, string>;
    error: string | null;
  };
  queries_7d: {
    count: number;
    answered: number;
    insufficient: number;
    avg_total_ms: number;
    avg_retrieval_ms: number;
    avg_generation_ms: number;
    citations: number;
  };
  evaluation_runs: number;
  recent_queries: QueryLog[];
  capabilities: {
    hybrid_retrieval: boolean;
    fts5: boolean;
    prompt_cache: boolean;
    prompt_cache_note: string;
  };
}

export interface Readiness {
  ready: boolean;
  checks: Record<string, { ok: boolean; count?: number | null; error?: string }>;
  timestamp: string;
}

export interface QueryLog {
  id: string;
  kind?: string;
  query_text: string;
  status: string;
  total_ms: number;
  retrieval_ms: number;
  generation_ms: number;
  citation_count: number;
  citations_valid: number | boolean;
  model?: string | null;
  provider?: string | null;
  created_at: string;
  candidate_count?: number;
  selected_count?: number;
  cache_status?: string;
}

export interface RetrievedSource {
  source_id: string;
  chunk_id: string;
  document_id: string;
  document_title: string;
  chunk_index: number;
  page_number?: number | null;
  section_title?: string | null;
  section_path?: string | null;
  text: string;
  excerpt: string;
  vector_score?: number | null;
  lexical_score?: number | null;
  fusion_score: number;
  vector_rank?: number | null;
  lexical_rank?: number | null;
}

export interface Citation {
  source_id: string;
  chunk_id: string;
  document_id: string;
  document_title: string;
  page_number?: number | null;
  section_title?: string | null;
  excerpt: string;
}

export interface RagTimings {
  retrieval_ms: number;
  generation_ms: number;
  total_ms: number;
}

export interface RagAnswer {
  status: "answered" | "insufficient_evidence" | "error";
  query: string;
  answer: string;
  grounded: boolean;
  citations: Citation[];
  sources: RetrievedSource[];
  warnings: string[];
  strategy: string;
  timings: RagTimings;
  usage: {
    prompt_tokens?: number | null;
    completion_tokens?: number | null;
    total_tokens?: number | null;
  };
  model?: string | null;
  provider?: string | null;
  cache_status: string;
}

export interface RetrievalOnly {
  query: string;
  sources: RetrievedSource[];
  warnings: string[];
  strategy: string;
  timings: RagTimings;
}

export interface PreviewChunk {
  index: number;
  text: string;
  character_count: number;
  estimated_tokens: number;
  page_number?: number | null;
  section_title?: string | null;
  overlap_prefix_characters: number;
}

export interface ChunkPreview {
  document_id?: string | null;
  source_characters: number;
  chunks: PreviewChunk[];
  stats: {
    chunk_count: number;
    shown_chunk_count: number;
    total_characters: number;
    average_chunk_characters: number;
    min_chunk_characters: number;
    max_chunk_characters: number;
    estimated_tokens: number;
    chunk_size: number;
    chunk_overlap: number;
    strategy: string;
  };
  warnings: string[];
}

export interface ChunkCompare {
  document_id?: string | null;
  source_characters: number;
  results: ChunkPreview[];
  warnings: string[];
}

export interface EvaluationDataset {
  id: string;
  name: string;
  description: string;
  builtin: boolean;
}

export interface EvaluationCase {
  id?: string;
  question: string;
  expected_keywords: string[];
  expected_chunk_ids: string[];
  notes?: string;
}

export interface SuggestedCase {
  case: EvaluationCase;
  rationale: string;
}

export interface EvaluationCaseResult {
  case_id: string;
  question: string;
  hit: boolean;
  reciprocal_rank: number;
  relevant_source_id?: string | null;
  source_count: number;
  status: string;
  citation_count: number;
  grounded: boolean;
  latency_ms: number;
  answer?: string | null;
  warnings: string[];
}

export interface EvaluationRun {
  id: string;
  dataset_id: string;
  status: "completed" | "failed";
  document_ids: string[];
  generate: boolean;
  metrics: {
    retrieval_hit_rate: number;
    mrr: number;
    answer_rate: number;
    grounded_rate: number;
    citation_coverage: number;
    avg_latency_ms: number;
    cases: number;
    hits: number;
  };
  details: EvaluationCaseResult[];
  duration_ms: number;
  created_at: string;
}

export interface EvaluationHistoryRun {
  id: string;
  dataset_id: string;
  document_id?: string | null;
  status: string;
  metrics: EvaluationRun["metrics"];
  duration_ms: number;
  created_at: string;
}

export interface FlashcardItemData {
  id: string;
  question: string;
  answer: string;
  difficulty?: string;
}

export interface QuizQuestionOption {
  id: string;
  text: string;
}

export interface QuizQuestionItemData {
  id: string;
  question: string;
  options: QuizQuestionOption[];
  correct_answer: string;
  explanation: string;
  difficulty: string;
}

export interface KnowledgeConceptItemData {
  id: string;
  name: string;
  description: string;
  concept_type: string;
}

export interface KnowledgeRelationshipItemData {
  id: string;
  source_concept: string;
  target_concept: string;
  relationship_type: string;
}

export interface KnowledgeGraphResultData {
  concepts: KnowledgeConceptItemData[];
  relationships: KnowledgeRelationshipItemData[];
}

// ---------------------------------------------------------------------------
// Operations
// ---------------------------------------------------------------------------

export const ragApi = {
  session: () => request<SessionUser>("/auth/session"),
  login: (email: string, password: string) =>
    request<SessionUser>("/auth/login", {
      method: "POST",
      body: jsonBody({ email, password }),
    }),
  register: (email: string, password: string, displayName: string) =>
    request<SessionUser>("/auth/register", {
      method: "POST",
      body: jsonBody({ email, password, display_name: displayName }),
    }),
  logout: () => request<{ status: string }>("/auth/logout", { method: "POST" }),

  overview: () => request<Overview>("/system/overview"),
  readiness: () => request<Readiness>("/system/ready"),
  recentQueries: (limit = 50) =>
    request<{ queries: QueryLog[]; cache_status: string }>(
      `/observability/queries?limit=${limit}`,
    ),

  documents: () => request<DocumentSummary[]>("/documents"),
  document: (id: string) => request<DocumentDetail>(`/documents/${encodeURIComponent(id)}`),
  documentChunks: (id: string, limit = 100, offset = 0) =>
    request<ChunkInspection>(
      `/documents/${encodeURIComponent(id)}/chunks?limit=${limit}&offset=${offset}`,
    ),
  upload: (file: File) => {
    const form = new FormData();
    form.append("file", file);
    return request<{ document_id: string; status: string; title: string }>("/documents/process", {
      method: "POST",
      body: form,
    });
  },
  retry: (id: string) =>
    request<{ status: string; document_id: string }>(
      `/documents/${encodeURIComponent(id)}/retry`,
      { method: "POST" },
    ),
  reindex: (id: string) =>
    request<{ status: string; document_id: string }>(
      `/documents/${encodeURIComponent(id)}/reindex`,
      { method: "POST" },
    ),
  deleteDocument: (id: string) =>
    request<{ status: string }>(`/documents/${encodeURIComponent(id)}`, { method: "DELETE" }),

  previewChunks: (body: {
    text?: string;
    document_id?: string;
    chunk_size: number;
    chunk_overlap: number;
    max_chunks: number;
  }) =>
    request<ChunkPreview>("/chunking/preview", {
      method: "POST",
      body: jsonBody(body),
    }),
  compareChunks: (body: {
    text?: string;
    document_id?: string;
    configs: { chunk_size: number; chunk_overlap: number; label?: string }[];
    max_chunks: number;
  }) =>
    request<ChunkCompare>("/chunking/compare", {
      method: "POST",
      body: jsonBody(body),
    }),

  retrieve: (body: {
    query: string;
    document_ids: string[];
    top_k: number;
    minimum_similarity: number;
  }) =>
    request<RetrievalOnly>("/rag/retrieve", {
      method: "POST",
      body: jsonBody({ ...body, generate: false }),
    }),
  ask: (body: {
    query: string;
    document_ids: string[];
    top_k: number;
    minimum_similarity: number;
  }) =>
    request<RagAnswer>("/rag/query", {
      method: "POST",
      body: jsonBody({ ...body, generate: true }),
    }),

  datasets: () => request<EvaluationDataset[]>("/evaluation/datasets"),
  suggestCases: (documentId: string, limit = 5) =>
    request<SuggestedCase[]>(
      `/evaluation/suggest?document_id=${encodeURIComponent(documentId)}&limit=${limit}`,
    ),
  runEvaluation: (body: {
    dataset_id: string;
    document_ids: string[];
    cases: EvaluationCase[];
    top_k: number;
    minimum_similarity: number;
    generate: boolean;
  }) =>
    request<EvaluationRun>("/evaluation/run", {
      method: "POST",
      body: jsonBody(body),
    }),
  evaluationHistory: (limit = 20) =>
    request<{ runs: EvaluationHistoryRun[] }>(`/evaluation/history?limit=${limit}`),

  getFlashcards: async (documentId: string): Promise<FlashcardItemData[]> => {
    try {
      const res = await request<{ status: string; materials: { flashcards?: { body: unknown } } | null }>(
        `/learning/${encodeURIComponent(documentId)}`,
      );
      if (!res || !res.materials || !res.materials.flashcards) return [];
      const body = res.materials.flashcards.body;
      const raw = typeof body === "string" ? JSON.parse(body) : body;
      if (!Array.isArray(raw)) return [];
      return raw.map((c: Record<string, unknown>, i: number) => ({
        id: String(c.id || `card-${i}`),
        question: String(c.question || ""),
        answer: String(c.answer || ""),
        difficulty: String(c.difficulty || "medium"),
      }));
    } catch {
      return [];
    }
  },
  generateFlashcards: (documentId: string) =>
    request<{ status: string; generated_content: string }>("/learning/generate", {
      method: "POST",
      body: jsonBody({ document_id: documentId, generator: "flashcards" }),
    }),
  addFlashcard: (
    documentId: string,
    card: { question: string; answer: string; difficulty: string },
  ) =>
    request<{ status: string; flashcard_id: string }>(
      `/learning/${encodeURIComponent(documentId)}/flashcards`,
      {
        method: "POST",
        body: jsonBody({ ...card, idempotency_key: `manual-${Date.now()}` }),
      },
    ),

  getQuiz: async (documentId: string): Promise<QuizQuestionItemData[]> => {
    try {
      const res = await request<{ status: string; materials: { quiz?: { body: unknown } } | null }>(
        `/learning/${encodeURIComponent(documentId)}`,
      );
      if (!res || !res.materials || !res.materials.quiz) return [];
      const body = res.materials.quiz.body;
      const raw = typeof body === "string" ? JSON.parse(body) : body;
      if (!Array.isArray(raw)) return [];
      return raw.map((q: Record<string, unknown>, i: number) => {
        let opts: QuizQuestionOption[] = [];
        if (Array.isArray(q.options)) {
          opts = q.options.map((o: unknown, oi: number) =>
            typeof o === "string"
              ? { id: ["A", "B", "C", "D"][oi] || String(oi + 1), text: o }
              : {
                  id: String(
                    (o as Record<string, unknown>)?.id ||
                      ["A", "B", "C", "D"][oi] ||
                      String(oi + 1),
                  ),
                  text: String((o as Record<string, unknown>)?.text || o),
                },
          );
        }
        return {
          id: String(q.id || `q-${i}`),
          question: String(q.question || ""),
          options: opts,
          correct_answer: String(q.correct_answer || ""),
          explanation: String(q.explanation || ""),
          difficulty: String(q.difficulty || "medium"),
        };
      });
    } catch {
      return [];
    }
  },
  generateQuiz: (documentId: string) =>
    request<{ status: string; generated_content: string }>("/learning/generate", {
      method: "POST",
      body: jsonBody({ document_id: documentId, generator: "quiz" }),
    }),
  addQuizQuestion: (
    documentId: string,
    question: {
      question: string;
      options: string[];
      correct_answer: string;
      explanation: string;
      difficulty: string;
    },
  ) =>
    request<{ status: string; quiz_id: string }>(
      `/learning/${encodeURIComponent(documentId)}/quizzes`,
      {
        method: "POST",
        body: jsonBody({ ...question, idempotency_key: `manual-${Date.now()}` }),
      },
    ),

  getKnowledgeGraph: async (documentId: string): Promise<KnowledgeGraphResultData> => {
    try {
      const res = await request<{
        concepts?: Record<string, unknown>[];
        relationships?: Record<string, unknown>[];
      }>(`/knowledge/${encodeURIComponent(documentId)}`);
      return {
        concepts: (res?.concepts || []).map((c) => ({
          id: String(c.id || ""),
          name: String(c.name || "Unknown"),
          description: String(c.description || ""),
          concept_type: String(c.concept_type || "CONCEPT"),
        })),
        relationships: (res?.relationships || []).map((r) => ({
          id: String(r.id || `${r.source_concept}->${r.target_concept}`),
          source_concept: String(r.source_concept || ""),
          target_concept: String(r.target_concept || ""),
          relationship_type: String(r.relationship_type || "RELATED_TO"),
        })),
      };
    } catch {
      return { concepts: [], relationships: [] };
    }
  },
  extractKnowledgeGraph: async (documentId: string): Promise<KnowledgeGraphResultData> => {
    const res = await request<{
      concepts?: Record<string, unknown>[];
      relationships?: Record<string, unknown>[];
    }>(`/knowledge/${encodeURIComponent(documentId)}/extract`, { method: "POST" });
    return {
      concepts: (res?.concepts || []).map((c) => ({
        id: String(c.id || ""),
        name: String(c.name || "Unknown"),
        description: String(c.description || ""),
        concept_type: String(c.concept_type || "CONCEPT"),
      })),
      relationships: (res?.relationships || []).map((r) => ({
        id: String(r.id || `${r.source_concept}->${r.target_concept}`),
        source_concept: String(r.source_concept || ""),
        target_concept: String(r.target_concept || ""),
        relationship_type: String(r.relationship_type || "RELATED_TO"),
      })),
    };
  },
};
