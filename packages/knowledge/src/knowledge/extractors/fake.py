import hashlib
from datetime import UTC, datetime

from content.chunking import ChunkCollection
from knowledge.concept import KnowledgeConcept
from knowledge.enums import ConceptType, RelationshipType
from knowledge.extractors.extraction_result import KnowledgeExtractionResult
from knowledge.extractors.interfaces import AbstractKnowledgeExtractor
from knowledge.extractors.provider_info import KnowledgeExtractorInfo
from knowledge.graph import KnowledgeGraph
from knowledge.metadata import KnowledgeMetadata
from knowledge.relationship import KnowledgeRelationship


class FakeKnowledgeExtractor(AbstractKnowledgeExtractor):
    """
    A deterministic mock knowledge extractor for development and testing.
    Generates a predictable knowledge graph without making external API calls.
    """

    def __init__(self, processing_delay_ms: int = 100) -> None:
        self.processing_delay_ms = processing_delay_ms
        self._info = KnowledgeExtractorInfo(
            extractor_id="fake_extractor",
            extractor_name="Fake Knowledge Extractor",
            version="1.0",
            provider="Development",
            supports_batch_processing=True,
            supports_streaming=False,
            maximum_chunks_per_request=1000,
            maximum_tokens=1000000,
            supports_relationship_extraction=True,
            supports_alias_extraction=True,
        )

    @property
    def info(self) -> KnowledgeExtractorInfo:
        return self._info

    def _generate_id(self, document_id: str, *parts: str) -> str:
        """Generate a deterministic ID based on document_id and parts."""
        hasher = hashlib.sha256()
        hasher.update(document_id.encode())
        for part in parts:
            hasher.update(part.encode())
        return hasher.hexdigest()

    async def extract(self, chunks: ChunkCollection) -> KnowledgeExtractionResult:
        """Generate deterministic fake concepts and relationships."""
        document_id = getattr(chunks, "document_id", "test-doc")

        metadata = KnowledgeMetadata(
            source_document=document_id,
            source_chunk="mock_chunk",
            language="en",
            confidence=0.99,
            extraction_version=self.info.version,
            created_by=self.info.extractor_id,
        )

        now = datetime.now(UTC)

        concept_names = ["Transformer", "Attention", "Encoder", "Decoder"]
        concepts: list[KnowledgeConcept] = []
        for name in concept_names:
            c_id = self._generate_id(document_id, "concept", name)
            concepts.append(
                KnowledgeConcept(
                    id=c_id,
                    document_id=document_id,
                    name=name,
                    description=f"A fake description for {name}",
                    concept_type=ConceptType.THEORY,
                    aliases=(),
                    confidence=0.95,
                    created_at=now,
                    metadata=metadata,
                )
            )

        relationships: list[KnowledgeRelationship] = []

        # Connect Transformer -> Attention
        r_id_1 = self._generate_id(document_id, "rel", concepts[0].id, concepts[1].id)
        relationships.append(
            KnowledgeRelationship(
                id=r_id_1,
                document_id=document_id,
                source_concept=concepts[0].id,
                target_concept=concepts[1].id,
                relationship_type=RelationshipType.USES,
                confidence=0.95,
                created_at=now,
                metadata=metadata,
            )
        )

        # Connect Transformer -> Encoder
        r_id_2 = self._generate_id(document_id, "rel", concepts[0].id, concepts[2].id)
        relationships.append(
            KnowledgeRelationship(
                id=r_id_2,
                document_id=document_id,
                source_concept=concepts[0].id,
                target_concept=concepts[2].id,
                relationship_type=RelationshipType.RELATED_TO,
                confidence=0.95,
                created_at=now,
                metadata=metadata,
            )
        )

        graph = KnowledgeGraph(
            concepts=tuple(concepts),
            relationships=tuple(relationships),
        )

        return KnowledgeExtractionResult(
            graph=graph,
            extractor_id=self.info.extractor_id,
            extractor_name=self.info.extractor_name,
            version=self.info.version,
            processing_time_ms=self.processing_delay_ms,
            processed_chunks=getattr(chunks, "total_chunks", 1),
            created_at=now,
        )

    async def extract_batch(
        self, collections: tuple[ChunkCollection, ...]
    ) -> tuple[KnowledgeExtractionResult, ...]:
        return tuple([await self.extract(c) for c in collections])
