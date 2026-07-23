import type { ApiRequestOptions, ApiResponse } from "./types";
import { ApiError, NetworkError, TimeoutError } from "./errors";

type Middleware = (req: Request) => Promise<Request> | Request;
type ResponseInterceptor = (res: Response) => Promise<Response> | Response;

class ApiClient {
  private baseUrl: string;
  private middlewares: Middleware[] = [];
  private interceptors: ResponseInterceptor[] = [];

  constructor(baseUrl: string = "") {
    this.baseUrl = baseUrl;
  }

  use(middleware: Middleware) {
    this.middlewares.push(middleware);
  }

  intercept(interceptor: ResponseInterceptor) {
    this.interceptors.push(interceptor);
  }

  async request<T>(endpoint: string, options: ApiRequestOptions = {}): Promise<ApiResponse<T>> {
    const { params, timeoutMs, retries = 0, ...customConfig } = options;
    
    let url = `${this.baseUrl}${endpoint}`;
    if (params) {
      const searchParams = new URLSearchParams();
      Object.entries(params).forEach(([key, value]) => searchParams.append(key, String(value)));
      url += `?${searchParams.toString()}`;
    }

    const config: RequestInit = {
      ...customConfig,
      headers: {
        "Content-Type": "application/json",
        ...customConfig.headers,
      },
    };

    let req = new Request(url, config);
    for (const middleware of this.middlewares) {
      req = await middleware(req);
    }

    let attempt = 0;
    while (attempt <= retries) {
      try {
        const controller = new AbortController();
        const id = timeoutMs ? setTimeout(() => controller.abort(), timeoutMs) : null;
        
        // If the caller provided a signal, link them
        if (config.signal) {
          config.signal.addEventListener("abort", () => controller.abort());
        }

        let response = await fetch(req, { ...config, signal: controller.signal });
        if (id) clearTimeout(id);

        for (const interceptor of this.interceptors) {
          response = await interceptor(response);
        }

        if (!response.ok) {
          throw new ApiError(response.status, response.statusText);
        }

        const data = await response.json() as T;
        return { data, status: response.status };

      } catch (error) {
        if (error instanceof ApiError && error.status < 500) {
          throw error; // Don't retry client errors
        }
        
        if (error instanceof DOMException && error.name === "AbortError") {
          // Determine if it was our timeout or the user's abort
          if (timeoutMs && attempt === retries) throw new TimeoutError();
          if (!timeoutMs) throw error; // Caller aborted
        }
        
        if (attempt >= retries) {
          if (error instanceof TypeError) throw new NetworkError();
          throw error;
        }
        
        attempt++;
        // Simple exponential backoff
        await new Promise(resolve => setTimeout(resolve, Math.pow(2, attempt) * 500));
      }
    }

    throw new Error("Unreachable");
  }

  get<T>(endpoint: string, options?: ApiRequestOptions) {
    return this.request<T>(endpoint, { ...options, method: "GET" });
  }

  post<T>(endpoint: string, data?: unknown, options?: ApiRequestOptions) {
    return this.request<T>(endpoint, {
      ...options,
      method: "POST",
      body: data ? JSON.stringify(data) : undefined,
    });
  }
}

export const apiClient = new ApiClient(process.env.NEXT_PUBLIC_API_URL || "");
