import type { ApiRequestOptions } from "./types";

/**
 * Standardized request policies dictating retry and timeout behaviors
 * for different types of operations across Kogniq.
 */
export const REQUEST_POLICIES = {
  // Authentication should never automatically retry to prevent lockouts.
  auth: {
    retries: 0,
    timeoutMs: 10000,
  } as ApiRequestOptions,

  // Document uploads are heavy and shouldn't silently retry to prevent duplicate processing.
  documentUpload: {
    retries: 0,
    timeoutMs: 60000, // 60s timeout for large files
  } as ApiRequestOptions,

  // Search queries are idempotent and can safely be retried if the network drops.
  search: {
    retries: 2,
    timeoutMs: 15000,
  } as ApiRequestOptions,

  // Retrieval and generation can be slow, but are idempotent.
  retrieval: {
    retries: 1,
    timeoutMs: 30000,
  } as ApiRequestOptions,
};
