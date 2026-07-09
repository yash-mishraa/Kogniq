from collections.abc import Iterator

from .exceptions import DuplicateProcessorError, InvalidProcessorError, ProcessorNotFoundError
from .interfaces import AbstractContentProcessor


class ProcessorRegistry:
    """
    Registry for managing content processors.
    Supports O(1) lookups by name, extension, and MIME type.
    """

    def __init__(self) -> None:
        self._name_map: dict[str, AbstractContentProcessor] = {}
        self._extension_map: dict[str, AbstractContentProcessor] = {}
        self._mime_map: dict[str, AbstractContentProcessor] = {}

    def register(self, processor: AbstractContentProcessor) -> None:
        """Registers a new processor. Raises exceptions on duplicates or invalid processors."""
        if not isinstance(processor, AbstractContentProcessor):
            raise InvalidProcessorError("Processor must implement AbstractContentProcessor.")

        info = processor.processor_info
        if not info:
            raise InvalidProcessorError("Processor must provide valid ProcessorInfo.")

        if info.name in self._name_map:
            raise DuplicateProcessorError(
                f"Processor with name '{info.name}' is already registered."
            )

        # Check for extension conflicts
        for ext in info.supported_extensions:
            if ext in self._extension_map:
                raise DuplicateProcessorError(
                    f"Extension '{ext}' is already registered by another processor."
                )

        # Check for MIME type conflicts
        for mime in info.supported_mime_types:
            if mime in self._mime_map:
                raise DuplicateProcessorError(
                    f"MIME type '{mime}' is already registered by another processor."
                )

        # Commit to registry
        self._name_map[info.name] = processor
        for ext in info.supported_extensions:
            self._extension_map[ext] = processor
        for mime in info.supported_mime_types:
            self._mime_map[mime] = processor

    def unregister(self, name: str) -> None:
        """Removes a processor by name."""
        if name not in self._name_map:
            raise ProcessorNotFoundError(f"Processor '{name}' not found.")

        processor = self._name_map[name]
        info = processor.processor_info

        # Remove from maps
        del self._name_map[name]

        for ext in info.supported_extensions:
            if ext in self._extension_map and self._extension_map[ext] is processor:
                del self._extension_map[ext]

        for mime in info.supported_mime_types:
            if mime in self._mime_map and self._mime_map[mime] is processor:
                del self._mime_map[mime]

    def get_by_extension(self, extension: str) -> AbstractContentProcessor:
        """Look up a processor by file extension (O(1))."""
        if extension not in self._extension_map:
            raise ProcessorNotFoundError(f"No processor registered for extension '{extension}'.")
        return self._extension_map[extension]

    def get_by_mime_type(self, mime_type: str) -> AbstractContentProcessor:
        """Look up a processor by MIME type (O(1))."""
        if mime_type not in self._mime_map:
            raise ProcessorNotFoundError(f"No processor registered for MIME type '{mime_type}'.")
        return self._mime_map[mime_type]

    def list_processors(self) -> list[AbstractContentProcessor]:
        """Return a list of all registered processors."""
        return list(self._name_map.values())

    def __contains__(self, name: str) -> bool:
        """Support 'name in registry' syntax."""
        return name in self._name_map

    def __len__(self) -> int:
        """Support len(registry) syntax."""
        return len(self._name_map)

    def __iter__(self) -> Iterator[AbstractContentProcessor]:
        """Support 'for processor in registry' syntax."""
        return iter(self._name_map.values())
