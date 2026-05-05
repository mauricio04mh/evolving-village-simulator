from dataclasses import dataclass
from typing import Optional


@dataclass
class Person:
    id: int
    sex: str  # "M" for male, "F" for female
    birth_time: float

    alive: bool = True

    partner_id: Optional[int] = None
    relationship_id: Optional[int] = None

    current_children: int = 0
    desired_children: int = 0

    pregnant: bool = False
    childbirth_time: Optional[float] = None
    pregnancy_father_id: Optional[int] = None

    available_for_partner: bool = True
    loneliness_end_time: Optional[float] = None

    death_token: int = 0
    partner_search_token: int = 0
    loneliness_token: int = 0
    pregnancy_token: int = 0

    def age(self, current_time: float) -> float:
        return current_time - self.birth_time