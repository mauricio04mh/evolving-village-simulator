from dataclasses import dataclass, field
from typing import Any


@dataclass(order=True)
class Event:
    time: float
    priority: int
    sequence: int
    event_type: str = field(compare=False)
    data: dict[str, Any] = field(default_factory=dict, compare=False)