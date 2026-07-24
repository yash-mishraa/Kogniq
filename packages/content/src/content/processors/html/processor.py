import time
from datetime import UTC, datetime

from ...normalized.document import NormalizedDocument
from ...plugins.interfaces import AbstractContentProcessor
from ...plugins.processor_info import ProcessorInfo
from ...resource.handle import ResourceHandle
from .exceptions import HTMLInvalidStreamError
from .metadata import extract_metadata
from .parser import HTMLParser
from .statistics import HTMLProcessorStatistics


class HTMLProcessor(AbstractContentProcessor):
    @property
    def processor_info(self) -> ProcessorInfo:
        return ProcessorInfo(
            name="kogniq-html",
            version="1.0",
            supported_extensions=("html", "htm"),
            supported_mime_types=("text/html",),
            description="Extracts semantic content from HTML using BeautifulSoup4",
        )

    def process(self, handle: ResourceHandle) -> NormalizedDocument:
        start_time = time.perf_counter()
        stats = HTMLProcessorStatistics()

        try:
            with handle.stream_reference.open_stream() as f:
                stream_bytes = f.read()
        except Exception as e:
            raise HTMLInvalidStreamError(f"Failed to read HTML stream: {e}") from e

        parser = HTMLParser(stream_bytes)

        # parse() returns the single NormalizedPage and populates stats
        page, soup = parser.parse(stats)

        stats.processing_duration_ms = (time.perf_counter() - start_time) * 1000

        # Extract title and metadata
        title_meta, metadata = extract_metadata(soup, handle, stats)

        stats.character_count = sum(len(b.text) for b in page.blocks)

        return NormalizedDocument(
            id=handle.id,
            title=title_meta,
            pages=(page,),
            source=(
                handle.source.name.lower() if hasattr(handle.source, "name") else str(handle.source)
            ),
            checksum=handle.checksum.value,
            version=self.processor_info.version,
            created_at=datetime.now(UTC),
            metadata=metadata,
            statistics=stats.to_dict(),
        )
