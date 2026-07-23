import type { IAuthService, SessionData } from "../interfaces";

export class LiveAuthService implements IAuthService {
  async getSession(signal?: AbortSignal): Promise<SessionData | null> {
    try {
      const response = await fetch("/api/v1/auth/session", { signal });
      if (response.ok) {
        return await response.json() as SessionData;
      }
      return null;
    } catch (error) {
      if (error instanceof Error && error.name === "AbortError") {
        throw error;
      }
      return null;
    }
  }

  async login(email: string, password: string): Promise<void> {
    const params = new URLSearchParams();
    params.append("username", email);
    params.append("password", password);
    
    const response = await fetch("/api/v1/auth/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded"
      },
      body: params
    });

    if (!response.ok) {
      throw new Error("Login failed");
    }
  }
}
