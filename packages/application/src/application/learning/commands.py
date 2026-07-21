from dataclasses import dataclass


@dataclass(frozen=True)
class GenerateLearningCommand:
    user_id: str
    document_id: str
    generator: str
