export class ApiError extends Error {
  constructor(
    public readonly status: number,
    public readonly message: string,
    public readonly code?: string
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export class NetworkError extends Error {
  constructor(message = "Unable to connect to the server right now.") {
    super(message);
    this.name = "NetworkError";
  }
}

export class TimeoutError extends Error {
  constructor(message = "The request took too long. Please try again.") {
    super(message);
    this.name = "TimeoutError";
  }
}

/**
 * Transforms technical errors into the calm editorial tone used by the UI.
 */
export function formatEditorialError(error: unknown): string {
  if (error instanceof ApiError) {
    if (error.status === 401) return "Please authenticate to access this knowledge.";
    if (error.status === 403) return "You don't have permission to view this knowledge.";
    if (error.status === 404) return "We couldn't find what you were looking for.";
    return "Unable to retrieve this knowledge right now. Try again shortly.";
  }
  
  if (error instanceof NetworkError || error instanceof TimeoutError) {
    return error.message;
  }
  
  if (error instanceof DOMException && error.name === "AbortError") {
    return "The request was cancelled.";
  }

  return "An unexpected disruption occurred. Please try again.";
}
