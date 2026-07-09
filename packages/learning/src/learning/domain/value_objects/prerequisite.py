from dataclasses import dataclass

from .identifiers import ConceptId


@dataclass(frozen=True)
class Prerequisite:
    """
    Represents a prerequisite dependency pointing to a Concept.
    """

    required_concept_id: ConceptId
    is_mandatory: bool = True
