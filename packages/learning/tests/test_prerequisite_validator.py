import pytest

from learning.domain.entities import Concept
from learning.domain.exceptions import CyclicPrerequisiteError
from learning.domain.services import PrerequisiteValidator
from learning.domain.value_objects import ConceptId, Prerequisite, TopicId, generate_id


def test_prerequisite_no_self_reference() -> None:
    c1_id = ConceptId(generate_id())
    with pytest.raises(CyclicPrerequisiteError):
        PrerequisiteValidator.ensure_no_cycles(c1_id, c1_id, [])


def test_prerequisite_cycle_detection() -> None:
    topic_id = TopicId(generate_id())
    c1 = Concept(topic_id=topic_id, name="C1", description="C1")
    c2 = Concept(topic_id=topic_id, name="C2", description="C2")
    c3 = Concept(topic_id=topic_id, name="C3", description="C3")

    # c1 depends on c2
    c1.add_prerequisite(Prerequisite(required_concept_id=c2.id))
    # c2 depends on c3
    c2.add_prerequisite(Prerequisite(required_concept_id=c3.id))

    # Now, trying to make c3 depend on c1 should raise cycle error
    all_concepts = [c1, c2, c3]
    with pytest.raises(CyclicPrerequisiteError):
        PrerequisiteValidator.ensure_no_cycles(
            target_concept_id=c3.id, new_prerequisite_id=c1.id, all_concepts=all_concepts
        )


def test_prerequisite_valid_addition() -> None:
    topic_id = TopicId(generate_id())
    c1 = Concept(topic_id=topic_id, name="C1", description="C1")
    c2 = Concept(topic_id=topic_id, name="C2", description="C2")

    # Valid
    PrerequisiteValidator.ensure_no_cycles(c1.id, c2.id, [c1, c2])
