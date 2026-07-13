import io
from datetime import UTC, datetime
from typing import Any

import pytest

from content.plugins.exceptions import (
    DuplicateExtensionError,
    DuplicateMimeTypeError,
    DuplicateProcessorError,
    InvalidProcessorDefinitionError,
    ProcessorNotFoundError,
    UnsupportedResourceError,
)
from content.plugins.interfaces import AbstractContentProcessor
from content.plugins.processor_info import ProcessorInfo
from content.plugins.registry import ProcessorRegistry
from content.resource import (
    AbstractStreamReference,
    Checksum,
    ChecksumAlgorithm,
    ContentSource,
    LifecycleState,
    ResourceHandle,
    ResourceMetadata as HandleMetadata,
)


class MemoryStreamReference(AbstractStreamReference):
    def __init__(self, data: bytes) -> None:
        self.data = data
    def open_stream(self) -> io.BytesIO:
        return io.BytesIO(self.data)

class DummyProcessor(AbstractContentProcessor):
    def __init__(
        self,
        name: str = "dummy",
        exts: tuple[str, ...] = ("ext",),
        mimes: tuple[str, ...] = ("mime/type",)
    ) -> None:
        self._info = ProcessorInfo(
            name=name,
            version="1.0",
            description="A dummy processor",
            supported_extensions=exts,
            supported_mime_types=mimes
        )
    @property
    def processor_info(self) -> ProcessorInfo:
        return self._info
    def process(self, handle: ResourceHandle) -> Any:
        return None

def test_registry_success() -> None:
    registry = ProcessorRegistry()
    proc = DummyProcessor("valid", ("ext1", ".ext2"), ("mime/type1", "mime/type2"))
    registry.register(proc)
    
    assert registry.processor_count() == 1
    assert registry.has_processor("valid")
    assert registry.is_supported(extension=".EXT1")
    assert registry.is_supported(mime_type="MIME/TYPE2")
    
    # Check normalization
    assert registry.processor_for_extension("EXT1") is proc
    assert registry.processor_for_extension(".ext1") is proc
    assert registry.processor_for_mime_type("MIME/TYPE1") is proc
    
    # Check introspection
    info = registry.processor_info("valid")
    assert info.name == "valid"
    
    # Check immutable returns
    exts = registry.supported_extensions()
    assert isinstance(exts, tuple)
    assert sorted(exts) == ["ext1", "ext2"]
    
def test_invalid_processor_definitions() -> None:
    registry = ProcessorRegistry()
    
    with pytest.raises(InvalidProcessorDefinitionError, match="Processor name"):
        registry.register(DummyProcessor(""))
        
    with pytest.raises(
        InvalidProcessorDefinitionError, match="must support at least one extension"
    ):
        registry.register(DummyProcessor("p", exts=()))
        
    with pytest.raises(InvalidProcessorDefinitionError, match="Duplicate extensions"):
        registry.register(DummyProcessor("p", exts=("ext", ".ext")))
        
    with pytest.raises(InvalidProcessorDefinitionError, match="Duplicate MIME types"):
        registry.register(DummyProcessor("p", mimes=("mime", "MIME")))

def test_duplicate_registrations() -> None:
    registry = ProcessorRegistry()
    proc1 = DummyProcessor("proc1", ("ext1",), ("mime1",))
    registry.register(proc1)
    
    # Same name
    with pytest.raises(DuplicateProcessorError):
        registry.register(DummyProcessor("proc1", ("ext2",), ("mime2",)))
        
    # Same extension
    with pytest.raises(DuplicateExtensionError):
        registry.register(DummyProcessor("proc2", ("ext1",), ("mime2",)))
        
    # Same mime
    with pytest.raises(DuplicateMimeTypeError):
        registry.register(DummyProcessor("proc3", ("ext3",), ("mime1",)))

def test_processor_for_resource() -> None:
    registry = ProcessorRegistry()
    proc = DummyProcessor("proc", ("txt",), ("text/plain",))
    registry.register(proc)
    
    handle1 = ResourceHandle(
        id="1", filename="a.txt", extension=".txt", mime_type="text/plain",
        source=ContentSource.UPLOAD,
        checksum=Checksum(algorithm=ChecksumAlgorithm.SHA256, value="1"),
        size_bytes=1, created_at=datetime.now(UTC), metadata=HandleMetadata(),
        stream_reference=MemoryStreamReference(b""), lifecycle_state=LifecycleState.CREATED
    )
    
    handle2 = ResourceHandle(
        id="2", filename="a.xyz", extension=".xyz", mime_type="text/plain",
        source=ContentSource.UPLOAD,
        checksum=Checksum(algorithm=ChecksumAlgorithm.SHA256, value="1"),
        size_bytes=1, created_at=datetime.now(UTC), metadata=HandleMetadata(),
        stream_reference=MemoryStreamReference(b""), lifecycle_state=LifecycleState.CREATED
    )
    
    handle3 = ResourceHandle(
        id="3", filename="a.xyz", extension=".xyz", mime_type="application/xyz",
        source=ContentSource.UPLOAD,
        checksum=Checksum(algorithm=ChecksumAlgorithm.SHA256, value="1"),
        size_bytes=1, created_at=datetime.now(UTC), metadata=HandleMetadata(),
        stream_reference=MemoryStreamReference(b""), lifecycle_state=LifecycleState.CREATED
    )
    
    # Matches by extension
    assert registry.processor_for_resource(handle1) is proc
    
    # Matches by mime type fallback
    assert registry.processor_for_resource(handle2) is proc
    
    # No match
    with pytest.raises(UnsupportedResourceError):
        registry.processor_for_resource(handle3)

def test_unknown_lookups() -> None:
    registry = ProcessorRegistry()
    with pytest.raises(ProcessorNotFoundError):
        registry.processor_for_extension("pdf")
    with pytest.raises(ProcessorNotFoundError):
        registry.processor_for_mime_type("application/pdf")
    with pytest.raises(ProcessorNotFoundError):
        registry.processor_for_name("unknown")
    with pytest.raises(ProcessorNotFoundError):
        registry.processor_info("unknown")
