from dataclasses import dataclass, field
from typing import Any


@dataclass
class RetrieverDocument:
    id: str
    score: float
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)
