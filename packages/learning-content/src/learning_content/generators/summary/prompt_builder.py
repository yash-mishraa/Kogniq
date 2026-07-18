from knowledge.graph import KnowledgeGraph

from content.chunking import ChunkCollection


class SummaryPromptBuilder:
    """
    Deterministically builds prompts for the Summary Generator.
    """

    def build(self, chunks: ChunkCollection, graph: KnowledgeGraph) -> str:
        """
        Build a deterministic summary prompt from chunks and knowledge graph.

        Args:
            chunks: The source chunks.
            graph: The extracted knowledge graph.

        Returns:
            The complete prompt string.
        """
        parts = [
            self._build_system(),
            self._build_objective(),
            self._build_concepts(graph),
            self._build_relationships(graph),
            self._build_source_content(chunks),
            self._build_output_requirements(),
        ]

        # Filter out empty parts and join
        return "\n\n".join(filter(None, parts)).strip()

    def _build_system(self) -> str:
        return "SYSTEM\nYou are an expert educational assistant."

    def _build_objective(self) -> str:
        return (
            "OBJECTIVE\nProduce a concise educational summary.\n"
            "Ensure that you cover the main ideas and integrate the key concepts provided."
        )

    def _build_concepts(self, graph: KnowledgeGraph) -> str:
        if not graph.concepts:
            return ""

        lines = ["KEY CONCEPTS"]
        lines.extend(
            f"- {concept.title}: {concept.description}"
            for concept in sorted(graph.concepts, key=lambda c: c.id)
        )

        return "\n".join(lines)

    def _build_relationships(self, graph: KnowledgeGraph) -> str:
        if not graph.relationships:
            return ""

        lines = ["RELATIONSHIPS"]
        lines.extend(
            f"- {rel.source_concept} --[{rel.relationship_type.name}]--> {rel.target_concept}"
            for rel in sorted(
                graph.relationships, key=lambda r: (r.source_concept, r.target_concept)
            )
        )

        return "\n".join(lines)

    def _build_source_content(self, chunks: ChunkCollection) -> str:
        if not chunks.chunks:
            return "SOURCE MATERIAL\n(No content provided)"

        lines = ["SOURCE MATERIAL"]
        lines.extend(chunk.text.strip() for chunk in chunks.chunks)

        return "\n".join(lines)

    def _build_output_requirements(self) -> str:
        return (
            "OUTPUT REQUIREMENTS\n"
            "- concise\n"
            "- accurate\n"
            "- no hallucinations\n"
            "- markdown allowed"
        )
