from knowledge.graph import KnowledgeGraph

from learning_content.generators.base import AbstractPromptBuilder, GenerationContext

PROMPT_VERSION = "explanation-v1"


class ExplanationPromptBuilder(AbstractPromptBuilder):
    """
    Deterministically builds prompts for the Explanation Generator.
    """

    def build(self, context: GenerationContext) -> str:
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
            "You are an expert educator who teaches concepts deeply rather than merely "
            "summarizing them. You use intuitive analogies whenever appropriate, explain "
            "difficult concepts using familiar examples, and avoid assuming prior knowledge "
            "unless absolutely necessary. You are technically accurate, highly educational, "
            "concise but complete, and you never hallucinate."
        )

    def _build_objective(self) -> str:
        return (
            "OBJECTIVE:\n"
            "Generate a structured, in-depth explanation that helps a student truly "
            "understand the topic."
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
            "OUTPUT REQUIREMENTS:\n"
            "Produce Markdown using EXACTLY the following headings:\n\n"
            "# Concept\n"
            "(Brief introduction)\n\n"
            "## Why It Matters\n"
            "(Where this is used in practice and why the student should care)\n\n"
            "## Intuition\n"
            "(An intuitive analogy or mental model)\n\n"
            "## Detailed Explanation\n"
            "(The core technical explanation)\n\n"
            "## Example\n"
            "(A concrete example or walk-through)\n\n"
            "## Common Mistakes\n"
            "(Misconceptions or errors to avoid)\n\n"
            "## Related Concepts\n"
            "(How this connects to other topics)\n\n"
            "## Key Takeaways\n"
            "(Bullet points summarizing the core ideas)\n\n"
            "Do not output anything before or after the markdown sections. Do not use "
            "unnecessary verbosity."
        )
