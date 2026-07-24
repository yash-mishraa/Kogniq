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

    const headers: Record<string, any> = {
      "Content-Type": "application/json",
      ...customConfig.headers,
    };

    // Some runtimes stringify undefined into "undefined" in Headers, so we must delete it entirely
    const contentTypeKey = Object.keys(headers).find(k => k.toLowerCase() === "content-type");
    if (contentTypeKey && headers[contentTypeKey] === undefined) {
      delete headers[contentTypeKey];
    }

    const config: RequestInit = {
      ...customConfig,
      headers,
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
    const isFormData = typeof FormData !== "undefined" && data instanceof FormData;
    const customHeaders = { ...options?.headers };

    // If it's FormData, let the browser set the Content-Type with boundary
    if (isFormData) {
      // Clean up Content-Type if it exists so browser handles it natively
      const headersKey = Object.keys(customHeaders).find(k => k.toLowerCase() === "content-type");
      if (headersKey) {
        delete (customHeaders as any)[headersKey];
      }
      // Set to undefined to override the default "application/json" in request()
      (customHeaders as any)["Content-Type"] = undefined;
    }

    return this.request<T>(endpoint, {
      ...options,
      headers: customHeaders,
      method: "POST",
      body: data ? (isFormData ? (data as FormData) : JSON.stringify(data)) : undefined,
    });
  }
}

export const apiClient = new ApiClient(process.env.NEXT_PUBLIC_API_URL || "");
