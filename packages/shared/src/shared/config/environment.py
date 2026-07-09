"""Runtime environment classification."""

from enum import StrEnum


class Environment(StrEnum):
    """Deployment-neutral names used to classify runtime behavior."""

    LOCAL = "local"
    TEST = "test"
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
