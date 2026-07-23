from fastapi import Response

from apps.api.app.config import APISettings


class SessionCookieHandler:
    def __init__(self, settings: APISettings) -> None:
        self.settings = settings

    def set_session_cookie(self, response: Response, session_id: str) -> None:
        """Set the session cookie with application-wide settings."""
        response.set_cookie(
            key=self.settings.session_cookie_name,
            value=session_id,
            max_age=self.settings.session_cookie_max_age,
            expires=self.settings.session_cookie_max_age,
            httponly=True,
            secure=self.settings.session_cookie_secure,
            samesite="lax",
            path="/",
        )

    def clear_session_cookie(self, response: Response) -> None:
        """Clear the session cookie to revoke client-side session."""
        response.delete_cookie(
            key=self.settings.session_cookie_name,
            httponly=True,
            secure=self.settings.session_cookie_secure,
            samesite="lax",
            path="/",
        )
