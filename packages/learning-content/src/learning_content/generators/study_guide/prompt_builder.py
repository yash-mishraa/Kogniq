from learning_content.generators.base.interfaces import AbstractPromptBuilder
from learning_content.generators.base.models import GenerationContext

PROMPT_VERSION = "study-guide-v1"


class StudyGuidePromptBuilder(AbstractPromptBuilder):
    """
    Constructs the prompt for generating a Study Guide.
    """

    def build(self, context: GenerationContext) -> str:
        text = "\n\n".join(chunk.text for chunk in context.chunks.chunks[:10])
        return (
            f"Generate a comprehensive study guide based on the following text.\n\n"
            f"Text:\n{text}\n\n"
            f"Format as Markdown."
        )
