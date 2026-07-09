from dataclasses import dataclass, field
from datetime import UTC, datetime

from ..value_objects import AIMetadata, KnowledgeNodeId, generate_id


@dataclass
class KnowledgeNode:
    """
    Abstract/base domain concept for graph representation of knowledge.
    Allows subjects, topics, and concepts to be treated uniformly in a graph.
    """

    id: KnowledgeNodeId = field(default_factory=lambda: KnowledgeNodeId(generate_id()))
    reference_id: str = ""  # E.g., stringified ConceptId
    node_type: str = ""  # E.g., 'CONCEPT', 'TOPIC'
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    ai_metadata: AIMetadata = field(default_factory=AIMetadata)

    def __post_init__(self) -> None:
        if not self.reference_id or not self.node_type:
            raise ValueError("KnowledgeNode requires reference_id and node_type.")
