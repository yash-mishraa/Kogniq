import datetime

from ..domain.entities import LearningResource
from ..domain.enums import ProcessingStatus
from ..domain.events import (
    DomainEvent,
    ResourceProcessingCompleted,
    ResourceProcessingFailed,
    ResourceProcessingStarted,
    ResourceValidated,
)
from ..domain.results import ProcessingResult
from ..domain.value_objects import ContentStatistics, ResourceMetadata
from .interfaces import (
    ChunkGenerator,
    ContentParser,
    ContentValidator,
    MetadataExtractor,
    SectionExtractor,
    StatisticsExtractor,
)


class ContentProcessingPipeline:
    """
    Orchestrates the transformation of raw learning resources into semantic chunks.
    Maintains pure orchestration without concrete implementation leakages.
    """

    def __init__(
        self,
        validator: ContentValidator,
        parser: ContentParser,
        metadata_extractor: MetadataExtractor,
        section_extractor: SectionExtractor,
        chunk_generator: ChunkGenerator,
        statistics_extractor: StatisticsExtractor,
    ) -> None:
        self.validator = validator
        self.parser = parser
        self.metadata_extractor = metadata_extractor
        self.section_extractor = section_extractor
        self.chunk_generator = chunk_generator
        self.statistics_extractor = statistics_extractor

    def process(self, resource: LearningResource) -> ProcessingResult:
        start_time = datetime.datetime.now(datetime.UTC)
        events: list[DomainEvent] = []

        try:
            # 1. Validation
            resource.status = ProcessingStatus.VALIDATING
            is_valid, validation_msg = self.validator.validate(resource)
            events.append(
                ResourceValidated(
                    resource_id=resource.id, is_valid=is_valid, validation_message=validation_msg
                )
            )

            if not is_valid:
                resource.status = ProcessingStatus.FAILED
                events.append(
                    ResourceProcessingFailed(resource_id=resource.id, error_message=validation_msg)
                )
                return self._create_empty_result(resource, events, start_time)

            resource.status = ProcessingStatus.VALIDATED

            # 2. Parsing
            resource.status = ProcessingStatus.PROCESSING
            events.append(ResourceProcessingStarted(resource_id=resource.id))
            parsed_content = self.parser.parse(resource)

            # 3. Extract Metadata
            metadata = self.metadata_extractor.extract_metadata(resource, parsed_content)

            # 4. Extract Sections
            sections = self.section_extractor.extract_sections(resource, parsed_content)

            # 5. Generate Chunks
            chunks = self.chunk_generator.generate_chunks(resource, sections, parsed_content)

            # 6. Extract Statistics
            statistics = self.statistics_extractor.extract_statistics(resource, sections, chunks)

            # 7. Complete
            resource.status = ProcessingStatus.PROCESSED
            events.append(
                ResourceProcessingCompleted(
                    resource_id=resource.id,
                    sections_extracted=len(sections),
                    chunks_generated=len(chunks),
                )
            )

            return ProcessingResult(
                resource=resource,
                metadata=metadata,
                statistics=statistics,
                sections=sections,
                chunks=chunks,
                events=events,
                processing_time=datetime.datetime.now(datetime.UTC) - start_time,
            )

        except Exception as e:
            resource.status = ProcessingStatus.FAILED
            events.append(ResourceProcessingFailed(resource_id=resource.id, error_message=str(e)))
            return self._create_empty_result(resource, events, start_time)

    def _create_empty_result(
        self, resource: LearningResource, events: list[DomainEvent], start_time: datetime.datetime
    ) -> ProcessingResult:
        return ProcessingResult(
            resource=resource,
            metadata=ResourceMetadata(language=resource.language),
            statistics=ContentStatistics(),
            sections=[],
            chunks=[],
            events=events,
            processing_time=datetime.datetime.now(datetime.UTC) - start_time,
        )
