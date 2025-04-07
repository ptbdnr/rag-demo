from __future__ import annotations
from typing import Optional
from dataclasses import dataclass, asdict

@dataclass
class PageContent:
    """A class to represent the content of a page."""
    content: str
    title: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert the PageContent instance to a dictionary."""
        return asdict(self)
