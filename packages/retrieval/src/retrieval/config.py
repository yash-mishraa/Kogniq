from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RetrieverConfig:
    """
    Configuration options for semantic retrieval orchestrators.
    """

    default_top_k: int = 10
    similarity_threshold: float = 0.0  # 0.0 means accept anything, 1.0 means exact match
