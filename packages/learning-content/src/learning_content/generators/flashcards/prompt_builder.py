from knowledge.graph import KnowledgeGraph

from learning_content.generators.base import AbstractPromptBuilder, GenerationContext

PROMPT_VERSION = "flashcards-v1"


class FlashcardsPromptBuilder(AbstractPromptBuilder):
    """
    Deterministically builds prompts for the Flashcards Generator.
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
            "You are an expert educational flashcard creator. Your goal is to extract "
            "and synthesize the provided source material into highly effective, "
            "concise study flashcards."
        )

    def _build_objective(self) -> str:
        return (
            "OBJECTIVE:\n"
            "Generate structured flashcards covering the core facts, definitions, and principles. "
            "Flashcards must be exam-oriented, factual, and strictly one concept per card "
            "with no duplicates."
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
            "You must respond ONLY with a valid, raw JSON array of objects. "
            "Do NOT include any Markdown, do NOT wrap the response in ```json fences, "
            "and do NOT include any explanatory text before or after the JSON.\n\n"
            "The JSON array must match this schema:\n"
            "[\n"
            "  {\n"
            '    "question": "...",\n'
            '    "answer": "...",\n'
            '    "difficulty": "easy" | "medium" | "hard"\n'
            "  }\n"
            "]\n\n"
            "INSTRUCTIONS:\n"
            "- Strictly preserve technical accuracy and avoid hallucinations.\n"
            "- Do not include duplicate questions."
        )
