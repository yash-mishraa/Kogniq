export interface SessionUser {
  id: string;
  email: string;
}

export interface SessionData {
  user: SessionUser;
}

export interface IAuthService {
  getSession(): Promise<SessionData | null>;
  login(email: string, password: string): Promise<void>;
}
