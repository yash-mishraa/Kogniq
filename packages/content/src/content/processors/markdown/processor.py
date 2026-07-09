import time
from datetime import UTC, datetime

from ...normalized.document import NormalizedDocument
from ...plugins.interfaces import AbstractContentProcessor
from ...plugins.processor_info import ProcessorInfo
from ...resource.handle import ResourceHandle
from .metadata import extract_metadata
from .parser import MarkdownItParser
from .statistics import MarkdownProcessorStatistics


class MarkdownProcessor(AbstractContentProcessor):
    @property
    def processor_info(self) -> ProcessorInfo:
        return ProcessorInfo(
            name="kogniq-markdown",
            version="1.0",
            supported_extensions=("md", "markdown", "txt"),
            supported_mime_types=("text/markdown", "text/plain"),
            description="Extracts semantic content from Markdown using markdown-it-py",
        )

    def process(self, handle: ResourceHandle) -> NormalizedDocument:
        start_time = time.perf_counter()
        stats = MarkdownProcessorStatistics()

        with handle.stream_reference.open_stream() as f:
            stream_bytes = f.read()

        parser = MarkdownItParser(stream_bytes)
        
        pages = list(parser.iter_pages(stats))

        stats.processing_duration_ms = (time.perf_counter() - start_time) * 1000
        
        blocks = pages[0].blocks if pages else ()
        title_meta, metadata = extract_metadata(blocks)
        title = title_meta if title_meta else handle.filename

        return NormalizedDocument(
            id=handle.id,
            title=title,
            pages=tuple(pages),
            source=(
                str(handle.source.value) if hasattr(handle.source, "value") else str(handle.source)
            ),
            checksum=handle.checksum.value,
            version=self.processor_info.version,
            created_at=datetime.now(UTC),
            metadata=metadata,
            statistics=stats.to_dict(),
        )
