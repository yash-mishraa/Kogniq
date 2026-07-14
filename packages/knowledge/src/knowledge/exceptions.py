from shared.exceptions import KogniqError


class KnowledgeDomainError(KogniqError):
    """Base exception for all Knowledge Graph domain errors."""


class InvalidConceptError(KnowledgeDomainError):
    """Raised when a concept is improperly formed."""


class InvalidRelationshipError(KnowledgeDomainError):
    """Raised when a relationship is improperly formed."""


class InvalidGraphError(KnowledgeDomainError):
    """Raised when a graph is improperly formed."""
