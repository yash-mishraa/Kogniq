from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class NormalizedSpan:
    """Represents inline formatting within a text block."""

    text: str
    bold: bool = False
    italic: bool = False
    underline: bool = False
    monospace: bool = False
    hyperlink: str | None = None
    language: str | None = None
