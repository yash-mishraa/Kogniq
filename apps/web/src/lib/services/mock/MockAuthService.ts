import type { IAuthService, SessionData } from "../interfaces";

export class MockAuthService implements IAuthService {
  async getSession(): Promise<SessionData | null> {
    await new Promise((resolve) => setTimeout(resolve, 300));
    // Only return session if mock_session is set (simulating a login)
    if (typeof window !== "undefined" && localStorage.getItem("mock_session") === "true") {
      return {
        user: {
          id: "mock-user-1",
          email: "user@example.com"
        }
      };
    }
    return null;
  }

  async login(email: string, _password: string): Promise<void> {
    await new Promise((resolve) => setTimeout(resolve, 500));
    if (typeof window !== "undefined") {
      localStorage.setItem("mock_session", "true");
    }
  }
}
