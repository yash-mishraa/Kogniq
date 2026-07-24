import time
from datetime import UTC, datetime

from ...normalized.document import NormalizedDocument
from ...plugins.interfaces import AbstractContentProcessor
from ...plugins.processor_info import ProcessorInfo
from ...resource.handle import ResourceHandle
from .metadata import extract_metadata
from .parser import TxtParser
from .statistics import TXTProcessorStatistics


class TXTProcessor(AbstractContentProcessor):
    @property
    def processor_info(self) -> ProcessorInfo:
        return ProcessorInfo(
            name="kogniq-txt",
            version="1.0",
            supported_extensions=("txt",),
            supported_mime_types=("text/plain",),
            description="Extracts semantic content from Plain Text files using standard library",
        )

    def process(self, handle: ResourceHandle) -> NormalizedDocument:
        start_time = time.perf_counter()
        stats = TXTProcessorStatistics()

        with handle.stream_reference.open_stream() as f:
            stream_bytes = f.read()

        parser = TxtParser(stream_bytes)

        pages = list(parser.iter_pages(stats))

        stats.processing_duration_ms = (time.perf_counter() - start_time) * 1000

        blocks = pages[0].blocks if pages else ()
        title, metadata = extract_metadata(blocks, handle.filename)

        return NormalizedDocument(
            id=handle.id,
            title=title,
            pages=tuple(pages),
            source=(
                handle.source.name.lower() if hasattr(handle.source, "name") else str(handle.source)
            ),
            checksum=handle.checksum.value,
            version=self.processor_info.version,
            created_at=datetime.now(UTC),
            metadata=metadata,
            statistics=stats.to_dict(),
        )
