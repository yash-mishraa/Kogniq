import time
from datetime import UTC, datetime

from ...normalized.document import NormalizedDocument
from ...plugins.interfaces import AbstractContentProcessor
from ...plugins.processor_info import ProcessorInfo
from ...resource.handle import ResourceHandle
from .parser import PyMuPDFParser
from .statistics import PDFProcessorStatistics


class PDFProcessor(AbstractContentProcessor):
    @property
    def processor_info(self) -> ProcessorInfo:
        return ProcessorInfo(
            name="kogniq-pdf",
            version="1.0",
            supported_extensions=("pdf",),
            supported_mime_types=("application/pdf",),
            description="Extracts semantic content from PDFs using PyMuPDF",
        )

    def process(self, handle: ResourceHandle) -> NormalizedDocument:
        start_time = time.perf_counter()
        stats = PDFProcessorStatistics()

        with handle.stream_reference.open_stream() as f:
            stream_bytes = f.read()

        parser = PyMuPDFParser(stream_bytes)
        try:
            title_meta, metadata = parser.get_metadata()
            if title_meta or metadata.author:
                stats.metadata_available = True

            pages = []
            for page in parser.iter_pages():
                pages.append(page)
                stats.pages_processed += 1
                stats.blocks_extracted += len(page.blocks)

            stats.processing_duration_ms = (time.perf_counter() - start_time) * 1000

            title = title_meta
            if not title and pages:
                for block in pages[0].blocks:
                    text = block.text.strip()
                    if text:
                        title = text
                        break

            if not title:
                title = handle.filename

            return NormalizedDocument(
                id=handle.id,
                title=title,
                pages=tuple(pages),
                source=str(handle.source.value)
                if hasattr(handle.source, "value")
                else str(handle.source),
                checksum=handle.checksum.value,
                version=self.processor_info.version,
                created_at=datetime.now(UTC),
                metadata=metadata,
                statistics=stats.to_dict(),
            )
        finally:
            parser.close()
