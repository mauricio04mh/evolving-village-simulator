from dataclasses import dataclass
from typing import Optional


@dataclass
class SimulationCounters:
    total_deaths: int = 0
    total_births: int = 0
    total_couples_created: int = 0
    total_breakups: int = 0
    total_pregnancies: int = 0

    deaths_male: int = 0
    deaths_female: int = 0
    deaths_age_0_12: int = 0
    deaths_age_12_45: int = 0
    deaths_age_45_76: int = 0
    deaths_age_76_125: int = 0
    death_age_sum: float = 0.0
    death_age_count: int = 0

    total_birth_events: int = 0
    births_male: int = 0
    births_female: int = 0
    birth_events_single: int = 0
    birth_events_twins: int = 0
    birth_events_triplets: int = 0
    birth_events_quadruplets: int = 0
    birth_events_quintuplets: int = 0
    pregnancies_cancelled_by_maternal_death: int = 0

    total_widowhoods: int = 0
    relationship_duration_sum: float = 0.0
    relationship_duration_count: int = 0
    min_relationship_duration: Optional[float] = None
    max_relationship_duration: Optional[float] = None

    total_loneliness_periods_started: int = 0
    loneliness_duration_sum: float = 0.0
    loneliness_duration_count: int = 0
    min_loneliness_duration: Optional[float] = None
    max_loneliness_duration: Optional[float] = None

    processed_events: int = 0
    max_calendar_size: int = 0
    final_calendar_size: int = 0
    same_time_progress_warnings: int = 0

    def record_death(self, sex: str, age: float):
        self.total_deaths += 1

        if sex == "M":
            self.deaths_male += 1
        elif sex == "F":
            self.deaths_female += 1

        if age < 12:
            self.deaths_age_0_12 += 1
        elif age < 45:
            self.deaths_age_12_45 += 1
        elif age < 76:
            self.deaths_age_45_76 += 1
        else:
            self.deaths_age_76_125 += 1

        self.death_age_sum += age
        self.death_age_count += 1

    def record_birth_event(self, number_of_babies: int):
        self.total_birth_events += 1

        if number_of_babies == 1:
            self.birth_events_single += 1
        elif number_of_babies == 2:
            self.birth_events_twins += 1
        elif number_of_babies == 3:
            self.birth_events_triplets += 1
        elif number_of_babies == 4:
            self.birth_events_quadruplets += 1
        elif number_of_babies >= 5:
            self.birth_events_quintuplets += 1

    def record_birth(self, sex: str):
        self.total_births += 1

        if sex == "M":
            self.births_male += 1
        elif sex == "F":
            self.births_female += 1

    def record_relationship_duration(self, duration: float):
        self.relationship_duration_sum += duration
        self.relationship_duration_count += 1

        if (
            self.min_relationship_duration is None
            or duration < self.min_relationship_duration
        ):
            self.min_relationship_duration = duration

        if (
            self.max_relationship_duration is None
            or duration > self.max_relationship_duration
        ):
            self.max_relationship_duration = duration

    def record_loneliness_duration(self, duration: float):
        self.total_loneliness_periods_started += 1
        self.loneliness_duration_sum += duration
        self.loneliness_duration_count += 1

        if (
            self.min_loneliness_duration is None
            or duration < self.min_loneliness_duration
        ):
            self.min_loneliness_duration = duration

        if (
            self.max_loneliness_duration is None
            or duration > self.max_loneliness_duration
        ):
            self.max_loneliness_duration = duration
