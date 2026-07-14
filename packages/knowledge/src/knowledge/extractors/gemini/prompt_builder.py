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
                    "aliases": ["Alias1", "Alias2"]
                }
            ],
            "relationships": [
                {
                    "source": "source_concept_id",
                    "target": "target_concept_id",
                    "type": "RELATIONSHIP_TYPE"
                }
            ]
        }

        return f"""You are an expert knowledge extractor.
Extract educational concepts and their relationships from the following text.

Return your response strictly as a JSON object matching this schema:
{json.dumps(schema_format, indent=2)}

Use standard relationship types such as RELATED_TO, DEPENDS_ON, PREREQUISITE_FOR.

Text to analyze:
{text_content}"""
