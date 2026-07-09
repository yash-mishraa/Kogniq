"""Generic configuration provider contract."""

from typing import Protocol


class SettingsProvider[SettingsT_co](Protocol):
    """Produce an immutable settings object from an implementation-owned source."""

    def load(self) -> SettingsT_co:
        """Load and validate settings."""
        ...
