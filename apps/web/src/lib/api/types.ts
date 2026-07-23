export interface ApiRequestOptions extends RequestInit {
  timeoutMs?: number;
  params?: Record<string, string | number | boolean>;
  retries?: number;
}

export interface ApiResponse<T> {
  data: T;
  status: number;
}
