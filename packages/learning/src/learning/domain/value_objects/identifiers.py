import uuid
from typing import NewType

# Strongly typed identifiers to prevent passing a TopicId where a ConceptId is expected.
SubjectId = NewType("SubjectId", uuid.UUID)
TopicId = NewType("TopicId", uuid.UUID)
ConceptId = NewType("ConceptId", uuid.UUID)
LearningObjectiveId = NewType("LearningObjectiveId", uuid.UUID)
LearningResourceId = NewType("LearningResourceId", uuid.UUID)
QuestionId = NewType("QuestionId", uuid.UUID)
AssessmentId = NewType("AssessmentId", uuid.UUID)
KnowledgeNodeId = NewType("KnowledgeNodeId", uuid.UUID)
RevisionSessionId = NewType("RevisionSessionId", uuid.UUID)
LearningPathId = NewType("LearningPathId", uuid.UUID)


def generate_id() -> uuid.UUID:
    """Generate a new unique identifier."""
    return uuid.uuid4()
