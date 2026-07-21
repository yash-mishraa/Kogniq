from ..resource.handle import ResourceHandle
from .exceptions import (
    DuplicateExtensionError,
    DuplicateMimeTypeError,
    DuplicateProcessorError,
    InvalidProcessorDefinitionError,
    ProcessorNotFoundError,
    UnsupportedResourceError,
)
from .interfaces import AbstractContentProcessor
from .processor_info import ProcessorInfo


class ProcessorRegistry:
    """
    Registry for managing content processors.
    Supports O(1) lookups by name, extension, and MIME type.
    """

    def __init__(self) -> None:
        self._name_map: dict[str, AbstractContentProcessor] = {}
        self._extension_map: dict[str, AbstractContentProcessor] = {}
        self._mime_map: dict[str, AbstractContentProcessor] = {}

    def _normalize_extension(self, ext: str) -> str:
        return ext.lower().lstrip(".")

    def _normalize_mime_type(self, mime: str) -> str:
        return mime.lower().strip()

    def register(self, processor: AbstractContentProcessor) -> None:
        """Registers a new processor. Raises exceptions on duplicates or invalid definitions."""
        if not isinstance(processor, AbstractContentProcessor):
            raise InvalidProcessorDefinitionError(
                "Processor must implement AbstractContentProcessor."
            )

        info = processor.processor_info
        if not info:
            raise InvalidProcessorDefinitionError("Processor must provide valid ProcessorInfo.")

        if not info.name or not info.name.strip():
            raise InvalidProcessorDefinitionError("Processor name must not be empty.")

        if not info.version or not info.version.strip():
            raise InvalidProcessorDefinitionError("Processor version must not be empty.")

        if not info.description or not info.description.strip():
            raise InvalidProcessorDefinitionError("Processor description must not be empty.")

        if not info.supported_extensions:
            raise InvalidProcessorDefinitionError("Processor must support at least one extension.")

        if not info.supported_mime_types:
            raise InvalidProcessorDefinitionError("Processor must support at least one MIME type.")

        # Check for duplicate values within the processor definition
        normalized_exts = [self._normalize_extension(e) for e in info.supported_extensions]
        if len(set(normalized_exts)) != len(normalized_exts):
            raise InvalidProcessorDefinitionError(
                "Duplicate extensions found in processor definition."
            )

        normalized_mimes = [self._normalize_mime_type(m) for m in info.supported_mime_types]
        if len(set(normalized_mimes)) != len(normalized_mimes):
            raise InvalidProcessorDefinitionError(
                "Duplicate MIME types found in processor definition."
            )

        if info.name in self._name_map:
            raise DuplicateProcessorError(
                f"Processor with name '{info.name}' is already registered."
            )

        for ext in normalized_exts:
            if ext in self._extension_map:
                raise DuplicateExtensionError(
                    f"Extension '{ext}' is already registered by another processor."
                )

        for mime in normalized_mimes:
            if mime in self._mime_map:
                raise DuplicateMimeTypeError(
                    f"MIME type '{mime}' is already registered by another processor."
                )

        # Commit to registry
        self._name_map[info.name] = processor
        for ext in normalized_exts:
            self._extension_map[ext] = processor
        for mime in normalized_mimes:
            self._mime_map[mime] = processor

    def unregister(self, name: str) -> None:
        """Removes a processor by name."""
        if name not in self._name_map:
            raise ProcessorNotFoundError(f"Processor '{name}' not found.")

        processor = self._name_map[name]
        info = processor.processor_info

        del self._name_map[name]

        for ext in info.supported_extensions:
            norm_ext = self._normalize_extension(ext)
            if norm_ext in self._extension_map and self._extension_map[norm_ext] is processor:
                del self._extension_map[norm_ext]

        for mime in info.supported_mime_types:
            norm_mime = self._normalize_mime_type(mime)
            if norm_mime in self._mime_map and self._mime_map[norm_mime] is processor:
                del self._mime_map[norm_mime]

    def processor_for_extension(self, extension: str) -> AbstractContentProcessor:
        norm_ext = self._normalize_extension(extension)
        if norm_ext not in self._extension_map:
            raise ProcessorNotFoundError(f"No processor registered for extension '{extension}'.")
        return self._extension_map[norm_ext]

    def processor_for_mime_type(self, mime_type: str) -> AbstractContentProcessor:
        norm_mime = self._normalize_mime_type(mime_type)
        if norm_mime not in self._mime_map:
            raise ProcessorNotFoundError(f"No processor registered for MIME type '{mime_type}'.")
        return self._mime_map[norm_mime]

    def processor_for_name(self, name: str) -> AbstractContentProcessor:
        if name not in self._name_map:
            raise ProcessorNotFoundError(f"Processor '{name}' not found.")
        return self._name_map[name]

    def processor_for_resource(self, handle: ResourceHandle) -> AbstractContentProcessor:
        norm_ext = self._normalize_extension(handle.extension)
        if norm_ext in self._extension_map:
            return self._extension_map[norm_ext]

        norm_mime = self._normalize_mime_type(handle.mime_type)
        if norm_mime in self._mime_map:
            return self._mime_map[norm_mime]

        raise UnsupportedResourceError(
            f"No processor found for extension '{handle.extension}' "
            f"or MIME type '{handle.mime_type}'."
        )

    def processor_info(self, name: str) -> ProcessorInfo:
        return self.processor_for_name(name).processor_info

    def supported_extensions(self) -> tuple[str, ...]:
        return tuple(sorted(self._extension_map.keys()))

    def supported_mime_types(self) -> tuple[str, ...]:
        return tuple(sorted(self._mime_map.keys()))

    def available_processors(self) -> tuple[str, ...]:
        return tuple(self._name_map.keys())

    def processor_count(self) -> int:
        return len(self._name_map)

    def has_processor(self, name: str) -> bool:
        return name in self._name_map

    def is_supported(self, extension: str | None = None, mime_type: str | None = None) -> bool:
        if extension is not None and self._normalize_extension(extension) in self._extension_map:
            return True
        return mime_type is not None and self._normalize_mime_type(mime_type) in self._mime_map
