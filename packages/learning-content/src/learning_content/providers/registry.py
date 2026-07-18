from learning_content.providers.interfaces import AbstractLearningGenerator
from learning_content.providers.provider_info import GeneratorInfo
from learning_content.providers.registry_exceptions import (
    GeneratorNotFoundError,
    GeneratorRegistrationError,
)


class LearningGeneratorRegistry:
    """Registry for educational content generators with O(1) lookups."""

    def __init__(self) -> None:
        self._generators: dict[str, AbstractLearningGenerator] = {}

    def register(self, generator: AbstractLearningGenerator) -> None:
        """Register a new generator. Raises GeneratorRegistrationError if duplicate."""
        info = generator.info()
        if info.generator_id in self._generators:
            raise GeneratorRegistrationError(
                f"Generator with id '{info.generator_id}' is already registered."
            )
        self._generators[info.generator_id] = generator

    def generator_for_id(self, generator_id: str) -> AbstractLearningGenerator:
        """Retrieve a generator by ID. Raises GeneratorNotFoundError if not found."""
        try:
            return self._generators[generator_id]
        except KeyError as e:
            raise GeneratorNotFoundError(f"No generator found for id '{generator_id}'") from e

    def available_generators(self) -> tuple[GeneratorInfo, ...]:
        """Return info for all registered generators as an immutable tuple."""
        return tuple(g.info() for g in self._generators.values())

    def generator_count(self) -> int:
        """Return the total number of registered generators."""
        return len(self._generators)

    def has_generator(self, generator_id: str) -> bool:
        """Check if a generator ID is registered."""
        return generator_id in self._generators
