import json

from content.chunking import ChunkCollection


class GeminiPromptBuilder:
    """Builds prompts for Gemini knowledge extraction."""

    def build(self, chunks: ChunkCollection) -> str:
        """Construct a deterministic prompt from a collection of chunks."""
        text_content = "\n\n".join(chunk.text for chunk in chunks.chunks)

        schema_format = {
            "concepts": [
                {
                    "id": "unique_concept_id",
                    "title": "Concept Title",
                    "description": "Clear 2-3 sentence definition and educational explanation of this concept based on the document.",
                    "type": "ALGORITHM",
                    "aliases": ["Alias1", "Alias2"],
                }
            ],
            "relationships": [
                {
                    "source": "source_concept_id",
                    "target": "target_concept_id",
                    "type": "RELATED_TO",
                }
            ],
        }

        return f"""You are an expert knowledge extractor.
Extract the most important educational concepts and their meaningful relationships from the following text.
Ensure each concept has a clear, comprehensive description explaining what it is and its role in the text.

Return your response strictly as a JSON object matching this schema:
{json.dumps(schema_format, indent=2)}

Valid concept types: ALGORITHM, DEFINITION, PRINCIPLE, THEORY, DATA_STRUCTURE, FACT.
Valid relationship types: DEPENDS_ON, USES, DEFINES, REFERENCES, EXTENDS, IMPLEMENTS, EXPLAINS, RELATED_TO.

Text to analyze:
{text_content}"""
