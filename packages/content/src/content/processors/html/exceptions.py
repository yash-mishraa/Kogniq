from ...plugins.exceptions import ContentPluginError


class HTMLError(ContentPluginError):
    """Base exception for HTML processor errors."""


class HTMLEmptyError(HTMLError):
    """Raised when the HTML stream contains no meaningful content."""


class HTMLMalformedError(HTMLError):
    """Raised when the HTML cannot be parsed into a usable DOM."""


class HTMLInvalidStreamError(HTMLError):
    """Raised when the input stream cannot be read."""


class HTMLUnsupportedEncodingError(HTMLError):
    """Raised when the HTML stream uses an unsupported or invalid encoding."""
