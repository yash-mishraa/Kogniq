from knowledge.graph import KnowledgeGraph

from learning_content.generators.base import AbstractPromptBuilder, GenerationContext

PROMPT_VERSION = "notes-v1"


class NotesPromptBuilder(AbstractPromptBuilder):
    """
    Deterministically builds prompts for the Notes Generator.
    """

    def build(self, context: GenerationContext) -> str:
        """
        Build a deterministic notes prompt from chunks and knowledge graph.

        Args:
            context: The generation context containing chunks and graph.

        Returns:
            The complete prompt string.
        """
        parts = [
            self._build_system(),
            self._build_objective(),
            self._build_concepts(context.graph),
            self._build_relationships(context.graph),
            self._build_source_content(context),
            self._build_output_format(),
        ]
        return "\n\n".join(parts)

    def _build_system(self) -> str:
        return (
            "You are an expert educational note writer. Your goal is to synthesize "
            "the provided source material into highly structured, clear, and accurate study notes."
        )

    def _build_objective(self) -> str:
        return (
            "OBJECTIVE:\n"
            "Generate structured revision notes that cover the core facts, principles, "
            "and details of the source material. "
            "Organize information logically to facilitate rapid review."
        )

    def _build_concepts(self, graph: KnowledgeGraph) -> str:
        if not graph.concepts:
            return ""
        lines = ["KEY CONCEPTS:"]
        lines.extend(f"- {c.title}: {c.description}" for c in graph.concepts)
        return "\n".join(lines)

    def _build_relationships(self, graph: KnowledgeGraph) -> str:
        if not graph.relationships:
            return ""
        lines = ["RELATIONSHIPS:"]
        lines.extend(
            f"- {r.source_concept} {r.relationship_type.name} {r.target_concept}"
            for r in graph.relationships
        )
        return "\n".join(lines)

    def _build_source_content(self, context: GenerationContext) -> str:
        lines = ["SOURCE MATERIAL:"]
        for chunk in context.chunks.chunks:
            lines.append(f"--- Chunk {chunk.id} ---")
            lines.append(chunk.text)
        return "\n".join(lines)

    def _build_output_format(self) -> str:
        return (
            "OUTPUT FORMAT:\n"
            "Generate clean Markdown notes using the following exact headings structure:\n\n"
            "# [Main Topic Heading]\n\n"
            "## [Subtopic Heading]\n"
            "- Bullet Points\n\n"
            "### Important Facts\n"
            "[List of important facts]\n\n"
            "### Key Definitions\n"
            "[List of definitions]\n\n"
            "### Exam Tips\n"
            "[List of exam tips]\n\n"
            "### Common Mistakes\n"
            "[List of common mistakes]\n\n"
            "INSTRUCTIONS:\n"
            "- Strictly preserve technical accuracy and avoid hallucinations.\n"
            "- Avoid unnecessary verbosity.\n"
            "- Maintain clean formatting. Output only the requested Markdown."
        )
