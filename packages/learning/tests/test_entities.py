import pytest

from learning.domain.entities import (
    KnowledgeNode,
    Question,
    Subject,
    Topic,
)
from learning.domain.exceptions import InvalidQuestionEvaluationError
from learning.domain.value_objects import (
    SubjectId,
    generate_id,
)


def test_subject_validation() -> None:
    with pytest.raises(ValueError):
        Subject(name="", description="Test")


def test_topic_invariants() -> None:
    SubjectId(generate_id())
    with pytest.raises(ValueError):
        Topic(subject_id=None, name="Test", description="Test")  # type: ignore


def test_question_evaluation_invariant() -> None:
    with pytest.raises(InvalidQuestionEvaluationError):
        Question(prompt_text="What is X?", learning_objective_ids=set())


def test_knowledge_node_validation() -> None:
    with pytest.raises(ValueError):
        KnowledgeNode(reference_id="", node_type="")
