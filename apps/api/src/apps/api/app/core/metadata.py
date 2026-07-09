"""OpenAPI metadata construction."""

from apps.api.app.config import APISettings


def build_contact(settings: APISettings) -> dict[str, str]:
    """Build public contact metadata from configured values."""
    contact = {"name": settings.contact_name}
    if settings.contact_url:
        contact["url"] = settings.contact_url
    if settings.contact_email:
        contact["email"] = settings.contact_email
    return contact


def build_license(settings: APISettings) -> dict[str, str] | None:
    """Build license metadata only when a license has been selected."""
    if not settings.license_name:
        return None
    license_info = {"name": settings.license_name}
    if settings.license_url:
        license_info["url"] = settings.license_url
    return license_info


def build_servers(settings: APISettings) -> list[dict[str, str]]:
    """Serialize configured OpenAPI server entries."""
    return [server.model_dump() for server in settings.openapi_servers]
