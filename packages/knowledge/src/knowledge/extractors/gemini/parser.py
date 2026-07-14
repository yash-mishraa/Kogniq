import json
import logging

from knowledge.concept import KnowledgeConcept
from knowledge.enums import ConceptType, RelationshipType
from knowledge.extractors.gemini.exceptions import GeminiParsingError
from knowledge.graph import KnowledgeGraph
from knowledge.metadata import KnowledgeMetadata
from knowledge.relationship import KnowledgeRelationship

logger = logging.getLogger(__name__)


class GeminiResponseParser:
    """Parses JSON responses from Gemini into a KnowledgeGraph."""

    def parse(self, json_string: str, document_id: str = "unknown") -> KnowledgeGraph:
        """Parse the JSON string into an immutable KnowledgeGraph."""
        # Clean up markdown formatting if Gemini wrapped it in ```json
        cleaned = json_string.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError as e:
            raise GeminiParsingError(f"Failed to decode JSON: {e}") from e

        metadata = KnowledgeMetadata(
            source_document=document_id,
            source_chunk="extracted_batch",
            language="en",
            confidence=0.8,
            extraction_version="1.0",
            created_by="gemini",
        )

        concepts: dict[str, KnowledgeConcept] = {}
        relationships: dict[str, KnowledgeRelationship] = {}

        for item in data.get("concepts", []):
            try:
                c_id = str(item.get("id", "")).strip()
                title = str(item.get("title", "")).strip()
                if not c_id or not title:
                    continue
                    
                aliases_raw = item.get("aliases", [])
                aliases = tuple(str(a).strip() for a in aliases_raw if str(a).strip())
                
                # Prevent duplicates
                if c_id not in concepts:
                    concepts[c_id] = KnowledgeConcept(
                        id=c_id,
                        title=title,
                        description="",
                        concept_type=ConceptType.FACT,  # Default fallback
                        aliases=aliases,
                        metadata=metadata,
                    )
            except Exception as e:
                logger.warning(f"Skipping malformed concept: {e}")

        for item in data.get("relationships", []):
            try:
                source = str(item.get("source", "")).strip()
                target = str(item.get("target", "")).strip()
                rel_type_str = str(item.get("type", "")).strip().upper()
                
                if not source or not target or not rel_type_str:
                    continue
                    
                # Ensure both concepts actually exist in the graph
                if source not in concepts or target not in concepts:
                    continue
                    
                try:
                    rel_type = RelationshipType(rel_type_str)
                except ValueError:
                    rel_type = RelationshipType.RELATED_TO
                    
                r_id = f"{source}_{target}_{rel_type.value}"
                
                if r_id not in relationships:
                    relationships[r_id] = KnowledgeRelationship(
                        id=r_id,
                        source_concept=source,
                        target_concept=target,
                        relationship_type=rel_type,
                        confidence=0.8,
                        metadata=metadata,
                    )
            except Exception as e:
                logger.warning(f"Skipping malformed relationship: {e}")

        return KnowledgeGraph(
            concepts=tuple(concepts.values()),
            relationships=tuple(relationships.values()),
        )
