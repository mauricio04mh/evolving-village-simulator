from __future__ import annotations

from dataclasses import dataclass, field


AGE_BUCKETS = (
    (0, 12),
    (12, 15),
    (15, 21),
    (21, 35),
    (35, 45),
    (45, 60),
    (60, 76),
    (76, 125),
)


def safe_divide(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0

    return numerator / denominator


def average_or_zero(total: float, count: int) -> float:
    return safe_divide(total, count)


def age_bucket_suffix(start: int, end: int) -> str:
    return f"{start}_{end}"


def get_age_bucket(age: float):
    for index, (start, end) in enumerate(AGE_BUCKETS):
        is_last_bucket = index == len(AGE_BUCKETS) - 1

        if age < end or is_last_bucket:
            return start, end

    return AGE_BUCKETS[-1]


@dataclass
class StatisticsCollector:
    initial_population: int
    previous_total_population: int = field(init=False)
    previous_cumulative_totals: dict[str, int] = field(init=False)

    def __post_init__(self):
        self.previous_total_population = self.initial_population
        self.previous_cumulative_totals = {
            "total_births": 0,
            "total_deaths": 0,
            "total_pregnancies": 0,
            "total_couples_created": 0,
            "total_breakups": 0,
        }

    def collect(self, population, current_time, counters, alive_people=None):
        row = collect_statistics(
            population=population,
            current_time=current_time,
            counters=counters,
            alive_people=alive_people,
            previous_total_population=self.previous_total_population,
            previous_cumulative_totals=self.previous_cumulative_totals,
        )

        self.previous_total_population = row["total_population"]

        for key in self.previous_cumulative_totals:
            self.previous_cumulative_totals[key] = int(row[key])

        return row


def collect_statistics(
    population,
    current_time,
    counters,
    alive_people=None,
    previous_total_population=None,
    previous_cumulative_totals=None,
):
    if alive_people is None:
        alive_people = [person for person in population if person.alive]

    men = []
    women = []
    children = []
    adults_18_59 = []
    elderly = []
    fertile_women = []
    pregnant_women = []
    relationship_ids = set()
    age_bucket_counts = {}

    for start, end in AGE_BUCKETS:
        suffix = age_bucket_suffix(start, end)
        age_bucket_counts[f"count_age_{suffix}"] = 0
        age_bucket_counts[f"men_age_{suffix}"] = 0
        age_bucket_counts[f"women_age_{suffix}"] = 0
        age_bucket_counts[f"coupled_age_{suffix}"] = 0
        age_bucket_counts[f"pregnant_age_{suffix}"] = 0

    lonely_people = 0
    available_single_adults = 0
    unavailable_single_adults = 0
    adult_population = 0
    adults_in_couple = 0

    age_sum = 0.0

    for person in alive_people:
        age = person.age(current_time)
        age_sum += age

        if person.sex == "M":
            men.append(person)
        elif person.sex == "F":
            women.append(person)

        if age < 18:
            children.append(person)
        elif age < 60:
            adults_18_59.append(person)
        else:
            elderly.append(person)

        if person.sex == "F" and 12 <= age <= 44:
            fertile_women.append(person)

        if person.sex == "F" and person.pregnant:
            pregnant_women.append(person)

        if person.relationship_id is not None:
            relationship_ids.add(person.relationship_id)

        bucket_start, bucket_end = get_age_bucket(age)
        suffix = age_bucket_suffix(bucket_start, bucket_end)
        age_bucket_counts[f"count_age_{suffix}"] += 1

        if person.sex == "M":
            age_bucket_counts[f"men_age_{suffix}"] += 1
        elif person.sex == "F":
            age_bucket_counts[f"women_age_{suffix}"] += 1

        if person.relationship_id is not None:
            age_bucket_counts[f"coupled_age_{suffix}"] += 1

        if person.sex == "F" and person.pregnant:
            age_bucket_counts[f"pregnant_age_{suffix}"] += 1

        if age >= 12:
            adult_population += 1

            if person.relationship_id is not None:
                adults_in_couple += 1
            elif person.available_for_partner:
                available_single_adults += 1
            else:
                unavailable_single_adults += 1

        if (
            person.partner_id is None
            and not person.available_for_partner
            and person.loneliness_end_time is not None
        ):
            lonely_people += 1

    total_population = len(alive_people)
    men_count = len(men)
    women_count = len(women)
    pregnant_women_count = len(pregnant_women)
    couples = len(relationship_ids)
    average_age = average_or_zero(age_sum, total_population)

    previous_total_population = (
        total_population
        if previous_total_population is None
        else previous_total_population
    )
    previous_cumulative_totals = previous_cumulative_totals or {}

    births_this_year = counters.total_births - previous_cumulative_totals.get(
        "total_births",
        0,
    )
    deaths_this_year = counters.total_deaths - previous_cumulative_totals.get(
        "total_deaths",
        0,
    )
    pregnancies_this_year = (
        counters.total_pregnancies
        - previous_cumulative_totals.get("total_pregnancies", 0)
    )
    couples_created_this_year = (
        counters.total_couples_created
        - previous_cumulative_totals.get("total_couples_created", 0)
    )
    breakups_this_year = counters.total_breakups - previous_cumulative_totals.get(
        "total_breakups",
        0,
    )

    net_population_change = total_population - previous_total_population

    statistics = {
        "year": int(current_time),
        "total_population": total_population,
        "men": men_count,
        "women": women_count,
        "children": len(children),
        "adults": len(adults_18_59),
        "elderly": len(elderly),
        "fertile_women": len(fertile_women),
        "couples": couples,
        "pregnant_women": pregnant_women_count,
        "average_age": average_age,
        "total_births": counters.total_births,
        "total_deaths": counters.total_deaths,
        "total_pregnancies": counters.total_pregnancies,
        "total_couples_created": counters.total_couples_created,
        "total_breakups": counters.total_breakups,
        "births_this_year": births_this_year,
        "deaths_this_year": deaths_this_year,
        "pregnancies_this_year": pregnancies_this_year,
        "couples_created_this_year": couples_created_this_year,
        "breakups_this_year": breakups_this_year,
        "net_population_change": net_population_change,
        "sex_ratio": safe_divide(men_count, women_count),
        "couple_ratio": safe_divide(2 * couples, total_population),
        "pregnancy_ratio": safe_divide(pregnant_women_count, women_count),
        "birth_rate": safe_divide(births_this_year, total_population),
        "death_rate": safe_divide(deaths_this_year, total_population),
        "growth_rate": safe_divide(net_population_change, total_population),
        "deaths_male": counters.deaths_male,
        "deaths_female": counters.deaths_female,
        "deaths_age_0_12": counters.deaths_age_0_12,
        "deaths_age_12_45": counters.deaths_age_12_45,
        "deaths_age_45_76": counters.deaths_age_45_76,
        "deaths_age_76_125": counters.deaths_age_76_125,
        "death_age_sum": counters.death_age_sum,
        "death_age_count": counters.death_age_count,
        "average_death_age": average_or_zero(
            counters.death_age_sum,
            counters.death_age_count,
        ),
        "total_birth_events": counters.total_birth_events,
        "births_male": counters.births_male,
        "births_female": counters.births_female,
        "birth_events_single": counters.birth_events_single,
        "birth_events_twins": counters.birth_events_twins,
        "birth_events_triplets": counters.birth_events_triplets,
        "birth_events_quadruplets": counters.birth_events_quadruplets,
        "birth_events_quintuplets": counters.birth_events_quintuplets,
        "pregnancies_cancelled_by_maternal_death": (
            counters.pregnancies_cancelled_by_maternal_death
        ),
        "births_per_pregnancy": safe_divide(
            counters.total_births,
            counters.total_pregnancies,
        ),
        "births_per_birth_event": safe_divide(
            counters.total_births,
            counters.total_birth_events,
        ),
        "total_widowhoods": counters.total_widowhoods,
        "relationship_duration_sum": counters.relationship_duration_sum,
        "relationship_duration_count": counters.relationship_duration_count,
        "average_relationship_duration": average_or_zero(
            counters.relationship_duration_sum,
            counters.relationship_duration_count,
        ),
        "min_relationship_duration": (
            0.0
            if counters.min_relationship_duration is None
            else counters.min_relationship_duration
        ),
        "max_relationship_duration": (
            0.0
            if counters.max_relationship_duration is None
            else counters.max_relationship_duration
        ),
        "breakups_per_couple_created": safe_divide(
            counters.total_breakups,
            counters.total_couples_created,
        ),
        "widowhoods_per_couple_created": safe_divide(
            counters.total_widowhoods,
            counters.total_couples_created,
        ),
        "total_loneliness_periods_started": (
            counters.total_loneliness_periods_started
        ),
        "loneliness_duration_sum": counters.loneliness_duration_sum,
        "loneliness_duration_count": counters.loneliness_duration_count,
        "average_loneliness_duration": average_or_zero(
            counters.loneliness_duration_sum,
            counters.loneliness_duration_count,
        ),
        "min_loneliness_duration": (
            0.0
            if counters.min_loneliness_duration is None
            else counters.min_loneliness_duration
        ),
        "max_loneliness_duration": (
            0.0
            if counters.max_loneliness_duration is None
            else counters.max_loneliness_duration
        ),
        "lonely_people": lonely_people,
        "available_single_adults": available_single_adults,
        "unavailable_single_adults": unavailable_single_adults,
        "adult_population": adult_population,
        "adult_couple_ratio": safe_divide(adults_in_couple, adult_population),
        "processed_events": counters.processed_events,
        "max_calendar_size": counters.max_calendar_size,
        "final_calendar_size": counters.final_calendar_size,
        "same_time_progress_warnings": counters.same_time_progress_warnings,
    }

    statistics.update(age_bucket_counts)
    return statistics
