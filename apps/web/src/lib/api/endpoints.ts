export const ENDPOINTS = {
  auth: {
    login: "/api/v1/auth/login",
    logout: "/api/v1/auth/logout",
  },
  documents: {
    process: "/api/v1/documents/process",
    get: (id: string) => `/api/v1/documents/${id}`,
  },
  retrieval: {
    search: "/api/v1/retrieval/search",
  },
  learning: {
    generate: "/api/v1/learning/generate",
  },
} as const;
