import pytest

from education.domain import (
    ConceptType,
    EducationalConcept,
    EducationalDefinition,
    EducationalExample,
    EducationalExercise,
    EducationalObjective,
    EducationalRelationship,
    ExerciseType,
    InvalidConceptError,
    InvalidRelationshipError,
    RelationshipType,
)


def test_concept_valid() -> None:
    concept = EducationalConcept(
        id="c1", title="Machine Learning", concept_type=ConceptType.THEORETICAL
    )
    assert concept.id == "c1"
    assert concept.title == "Machine Learning"


def test_concept_invalid_title() -> None:
    with pytest.raises(InvalidConceptError, match="title cannot be empty"):
        EducationalConcept(id="c2", title="   ", concept_type=ConceptType.FACTUAL)


def test_definition_valid() -> None:
    definition = EducationalDefinition(id="d1", concept_id="c1", text="A subset of AI.")
    assert definition.concept_id == "c1"


def test_definition_invalid() -> None:
    with pytest.raises(InvalidConceptError, match="concept_id cannot be empty"):
        EducationalDefinition(id="d1", concept_id="", text="A subset of AI.")


def test_example_valid() -> None:
    example = EducationalExample(id="e1", concept_id="c1", content="Linear regression.")
    assert example.concept_id == "c1"


def test_exercise_valid() -> None:
    exercise = EducationalExercise(
        id="ex1",
        concept_ids=("c1", "c2"),
        exercise_type=ExerciseType.MULTIPLE_CHOICE,
        content="What is ML?",
    )
    assert "c1" in exercise.concept_ids


def test_exercise_invalid() -> None:
    with pytest.raises(InvalidConceptError, match="Exercises must reference at least one concept"):
        EducationalExercise(
            id="ex2", concept_ids=(), exercise_type=ExerciseType.SHORT_ANSWER, content="Define ML."
        )


def test_objective_invalid() -> None:
    with pytest.raises(InvalidConceptError, match="Objectives must reference at least one concept"):
        EducationalObjective(id="obj1", concept_ids=(), description="Understand ML.")


def test_relationship_valid() -> None:
    rel = EducationalRelationship(
        source_id="c1", target_id="c2", relationship_type=RelationshipType.PREREQUISITE
    )
    assert rel.source_id == "c1"
    assert rel.target_id == "c2"


def test_relationship_invalid_identical() -> None:
    with pytest.raises(InvalidRelationshipError, match="Source and target IDs cannot be identical"):
        EducationalRelationship(
            source_id="c1", target_id="c1", relationship_type=RelationshipType.SIMILAR_TO
        )
