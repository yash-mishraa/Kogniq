export const ENDPOINTS = {
  auth: {
    login: "/api/v1/auth/login",
    logout: "/api/v1/auth/logout",
  },
  documents: {
    process: "/api/v1/documents/process",
    get: (id: string) => `/api/v1/documents/${id}`,
    getAll: "/api/v1/documents",
    delete: (id: string) => `/api/v1/documents/${id}`,
  },
  resources: {
    list: "/api/v1/resources",
    get: (id: string) => `/api/v1/resources/${id}`,
    sections: (id: string) => `/api/v1/resources/${id}/sections`,
    chunks: (id: string) => `/api/v1/resources/${id}/chunks`,
    statistics: (id: string) => `/api/v1/resources/${id}/statistics`,
  },
  retrieval: {
    search: "/api/v1/retrieval/search",
  },
  learning: {
    generate: "/api/v1/learning/generate",
    get: (documentId: string) => `/api/v1/learning/${documentId}`,
  },
  student: {
    knowledgeStates: "/api/v1/student/knowledge-states",
    knowledgeState: (resourceId: string) => `/api/v1/student/knowledge-states/${resourceId}`,
    recommendations: "/api/v1/student/recommendations",
  },
} as const;
