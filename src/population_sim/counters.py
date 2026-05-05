from dataclasses import dataclass


@dataclass
class SimulationCounters:
    total_deaths: int = 0
    total_births: int = 0
    total_couples_created: int = 0
    total_breakups: int = 0
    total_pregnancies: int = 0