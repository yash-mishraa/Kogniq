from abc import ABC, abstractmethod


class AbstractTextGenerationProvider(ABC):
    """
    Abstract interface for text generation providers.
    
    This provider is purely for text generation and should not contain any
    business logic, prompt construction, or response parsing. It serves as
    a generic, reusable interface for all learning generators.
    """

    @property
    @abstractmethod
    def provider_id(self) -> str:
        """Get the unique identifier for this provider."""
        ...

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Get the specific model name being used."""
        ...

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """
        Generate text from a given prompt.
        
        Args:
            prompt: The complete string prompt.
            
        Returns:
            The raw generated text.
        """
        ...
