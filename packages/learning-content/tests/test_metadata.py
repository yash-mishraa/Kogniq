from learning_content.metadata import LearningContentMetadata


def test_learning_content_metadata_valid() -> None:
    metadata = LearningContentMetadata(
        provider="test_provider",
        model="test_model",
        model_version="1.0",
        generation_version="1.0",
        language="en",
        educational_level="beginner",
        subject="computer_science",
        syllabus="standard",
        prompt_version="1.0",
        tags=("test",),
    )
    assert metadata.provider == "test_provider"
    assert metadata.prompt_version == "1.0"


def test_learning_content_metadata_optional_fields() -> None:
    metadata = LearningContentMetadata(
        provider="test_provider",
        model="test_model",
        model_version="1.0",
        generation_version="1.0",
        language="en",
        educational_level="beginner",
        subject="computer_science",
        syllabus="standard",
        tags=("test",),
        prompt_version="2.0",
        template_version="3.0",
        generation_id="gen-123",
    )
    assert metadata.prompt_version == "2.0"
    assert metadata.template_version == "3.0"
    assert metadata.generation_id == "gen-123"
