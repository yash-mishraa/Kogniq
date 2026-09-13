from learning_content.providers.base import (
    AbstractTextGenerationProvider,
    TextGenerationProviderInfo,
)


class MockTextGenerationProvider(AbstractTextGenerationProvider):
    """
    Mock implementation of a text generation provider for testing and deterministic
    offline development.
    """

    def __init__(self) -> None:
        self._info = TextGenerationProviderInfo(
            provider_id="mock-provider",
            provider_name="Mock Provider",
            default_model="mock-model-v1",
            model_version="1.0",
            context_window=16000,
            supports_streaming=False,
            supports_json=True,
            supports_images=False,
            supports_tools=False,
        )

    @property
    def info(self) -> TextGenerationProviderInfo:
        return self._info

    def generate(
        self,
        prompt: str,
        *,
        temperature: float | None = None,  # noqa: ARG002
        max_tokens: int | None = None,  # noqa: ARG002
    ) -> str:
        lower = prompt.lower()
        if "flashcard" in lower:
            return (
                '[{"question": "What is self-attention?", '
                '"answer": "A mechanism that relates positions of a sequence."}]'
            )
        elif "multiple-choice" in lower or "quiz" in lower:
            return (
                '[{"question": "What is the primary function of the Transformer?", '
                '"options": ["To process images", "To replace RNNs and CNNs with self-attention", '
                '"To act as a database", "To compress audio"], '
                '"correct_answer": "To replace RNNs and CNNs with self-attention", '
                '"explanation": "The Transformer relies entirely on an attention mechanism to draw '
                'global dependencies between input and output.", '
                '"difficulty": "medium"}]'
            )
        elif "concept" in lower or "intuition" in lower or "explanation" in lower:
            return """# Concept
## Why It Matters
This is a mock why it matters.
## Intuition
This is a mock intuition.
## Detailed Explanation
This is a mock detailed explanation.
## Example
This is a mock example.
## Common Mistakes
This is a mock common mistake.
## Related Concepts
This is a mock related concept.
## Key Takeaways
- Mock takeaway 1
- Mock takeaway 2"""
        elif "study guide" in lower:
            return """# Comprehensive Study Guide
## 1. Introduction
This is a comprehensive study guide covering the main concepts.
## 2. Key Terms
- Attention
- Transformer
## 3. Review Questions
1. What is the role of positional encoding?"""
        elif "notes" in lower or "cornell" in lower:
            return """# Notes
## Cues
- Transformer
- Self-attention
## Notes
- The Transformer is a model architecture eschewing recurrence.
- Self-attention computes representations of a single sequence.
## Summary
The paper introduces the Transformer architecture based entirely on attention mechanisms."""
        elif "summary" in lower:
            return (
                "# Summary\n"
                "This is a concise summary of the provided text. The main focus "
                "is on the Transformer architecture which replaces RNNs and CNNs "
                "with self-attention mechanisms for sequence transduction tasks.\n"
            )
        return '{"title": "Fake Title", "content": "Fake content"}'
