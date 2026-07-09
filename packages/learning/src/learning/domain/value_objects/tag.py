from dataclasses import dataclass


@dataclass(frozen=True)
class Tag:
    """
    Represents an immutable, normalized metadata tag used to classify domain entities.
    """

    value: str

    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("Tag value cannot be empty.")
        # Normalize the tag: lowercase and stripped
        object.__setattr__(self, "value", self.value.strip().lower())
