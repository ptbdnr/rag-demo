from __future__ import annotations
from typing import Optional
from dataclasses import dataclass, asdict

@dataclass
class Chunk:
    """A class to represent a chunk of text."""
    text: str
    vector: Optional[list[float]] = None

    def to_dict(self) -> dict:
        """Convert the Chunk instance to a dictionary."""
        return asdict(self)