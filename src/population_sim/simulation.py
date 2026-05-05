import random

from population_sim.constants import (
    BIRTH,
    BREAKUP,
    COLLECT_STATISTICS,
    DEATH,
    DEATH_RISK_UPDATE,
    END_LONELINESS,
    PARTNER_ELIGIBILITY,
    PARTNER_SEARCH,
    PARTNER_SEARCH_RISK_UPDATE,
    PREGNANCY,
    PREGNANCY_RISK_UPDATE,
    PRIORITY_BIRTH,
    PRIORITY_BREAKUP,
    PRIORITY_DEATH,
    PRIORITY_PARTNER,
    PRIORITY_PREGNANCY,
    PRIORITY_STATISTICS,
)
from population_sim.counters import SimulationCounters
from population_sim.event_calendar import EventCalendar
from population_sim.person import Person
from population_sim.random_utils import (
    annual_probability_to_rate,
    event_occurs,
)
from population_sim.rules import (
    generate_desired_children,
    generate_number_of_babies,
    get_annual_death_probability,
    get_annual_partner_desire_probability,
    get_annual_pregnancy_probability,
    get_loneliness_mean_years,
    get_next_death_age_boundary,
    get_next_partner_desire_age_boundary,
    get_next_pregnancy_age_boundary,
    get_partner_formation_probability,
)
from population_sim.statistics import collect_statistics


class PopulationSimulation:
    def __init__(self, initial_women: int, initial_men: int, years: int = 100):
        self.initial_women = initial_women
        self.initial_men = initial_men
        self.years = years
        self.end_time = float(years)

        self.current_time = 0.0

        self.population = []
        self.yearly_statistics = []

        self.calendar = EventCalendar(end_time=self.end_time)
        self.counters = SimulationCounters()

        self.next_person_id = 0
        self.next_relationship_id = 0

        self._create_initial_population()
        self._schedule_statistics_events()

    # -------------------------------------------------
    # Main execution
    # -------------------------------------------------

    def run(self):
        while self.calendar.has_events():
            event = self.calendar.pop_next()

            if event.time > self.end_time:
                break

            self.current_time = event.time
            self._process_event(event.event_type, event.data)

        return self.yearly_statistics

    def _process_event(self, event_type: str, data: dict):
        if event_type == DEATH:
            self._process_death_event(data)

        elif event_type == DEATH_RISK_UPDATE:
            self._process_death_risk_update_event(data)

        elif event_type == PARTNER_ELIGIBILITY:
            self._process_partner_eligibility_event(data)

        elif event_type == PARTNER_SEARCH:
            self._process_partner_search_event(data)

        elif event_type == PARTNER_SEARCH_RISK_UPDATE:
            self._process_partner_search_risk_update_event(data)

        elif event_type == BREAKUP:
            self._process_breakup_event(data)

        elif event_type == END_LONELINESS:
            self._process_end_loneliness_event(data)

        elif event_type == PREGNANCY:
            self._process_pregnancy_event(data)

        elif event_type == PREGNANCY_RISK_UPDATE:
            self._process_pregnancy_risk_update_event(data)

        elif event_type == BIRTH:
            self._process_birth_event(data)

        elif event_type == COLLECT_STATISTICS:
            self._collect_yearly_statistics()

    # -------------------------------------------------
    # Population creation
    # -------------------------------------------------

    def _create_initial_population(self):
        for _ in range(self.initial_women):
            initial_age = random.uniform(0, 100)
            self._add_person(sex="F", age=initial_age)

        for _ in range(self.initial_men):
            initial_age = random.uniform(0, 100)
            self._add_person(sex="M", age=initial_age)

    def _add_person(self, sex: str, age: float):
        person = Person(
            id=self.next_person_id,
            sex=sex,
            birth_time=self.current_time - age,
            desired_children=generate_desired_children(),
        )

        self.population.append(person)
        self.next_person_id += 1

        self._schedule_death_or_death_risk_update(person)
        self._schedule_partner_search_or_eligibility(person)

        return person

    def _get_person_by_id(self, person_id: int):
        for person in self.population:
            if person.id == person_id:
                return person

        return None

    def get_alive_people(self):
        return [person for person in self.population if person.alive]

    # -------------------------------------------------
    # Death events
    # -------------------------------------------------

    def _schedule_death_or_death_risk_update(self, person: Person):
        if not person.alive:
            return

        person.death_token += 1
        token = person.death_token

        age = person.age(self.current_time)
        annual_probability = get_annual_death_probability(age, person.sex)
        rate = annual_probability_to_rate(annual_probability)

        next_boundary = get_next_death_age_boundary(age)

        if next_boundary is None:
            time_to_boundary = None
        else:
            time_to_boundary = next_boundary - age

        if rate <= 0:
            if time_to_boundary is not None:
                self.calendar.schedule(
                    time=self.current_time + time_to_boundary,
                    priority=PRIORITY_DEATH,
                    event_type=DEATH_RISK_UPDATE,
                    data={
                        "person_id": person.id,
                        "token": token,
                    },
                )
            return

        time_to_death = random.expovariate(rate)

        if time_to_boundary is not None and time_to_death >= time_to_boundary:
            self.calendar.schedule(
                time=self.current_time + time_to_boundary,
                priority=PRIORITY_DEATH,
                event_type=DEATH_RISK_UPDATE,
                data={
                    "person_id": person.id,
                    "token": token,
                },
            )
        else:
            self.calendar.schedule(
                time=self.current_time + time_to_death,
                priority=PRIORITY_DEATH,
                event_type=DEATH,
                data={
                    "person_id": person.id,
                    "token": token,
                },
            )

    def _process_death_event(self, data: dict):
        person = self._get_person_by_id(data["person_id"])

        if person is None:
            return

        if not person.alive:
            return

        if person.death_token != data["token"]:
            return

        person.alive = False
        self.counters.total_deaths += 1

        person.partner_search_token += 1

        if person.pregnant:
            person.pregnant = False
            person.childbirth_time = None
            person.pregnancy_father_id = None
            person.pregnancy_token += 1

        if person.partner_id is not None:
            self._handle_widowhood(person)

        person.partner_id = None
        person.relationship_id = None
        person.available_for_partner = False

    def _process_death_risk_update_event(self, data: dict):
        person = self._get_person_by_id(data["person_id"])

        if person is None:
            return

        if not person.alive:
            return

        if person.death_token != data["token"]:
            return

        self._schedule_death_or_death_risk_update(person)

    def _handle_widowhood(self, dead_person: Person):
        partner = self._get_person_by_id(dead_person.partner_id)

        if partner is None:
            return

        if not partner.alive:
            return

        partner.partner_id = None
        partner.relationship_id = None

        if not partner.pregnant:
            partner.pregnancy_token += 1

        self._start_loneliness_period(partner)

    # -------------------------------------------------
    # Partner events
    # -------------------------------------------------

    def _schedule_partner_search_or_eligibility(self, person: Person):
        if not person.alive:
            return

        if person.partner_id is not None:
            return

        if not person.available_for_partner:
            return

        age = person.age(self.current_time)

        person.partner_search_token += 1
        token = person.partner_search_token

        if age < 12:
            self.calendar.schedule(
                time=self.current_time + (12 - age),
                priority=PRIORITY_PARTNER,
                event_type=PARTNER_ELIGIBILITY,
                data={
                    "person_id": person.id,
                    "token": token,
                },
            )
            return

        annual_probability = get_annual_partner_desire_probability(age)
        rate = annual_probability_to_rate(annual_probability)

        next_boundary = get_next_partner_desire_age_boundary(age)

        if next_boundary is None:
            time_to_boundary = None
        else:
            time_to_boundary = next_boundary - age

        if rate <= 0:
            if time_to_boundary is not None:
                self.calendar.schedule(
                    time=self.current_time + time_to_boundary,
                    priority=PRIORITY_PARTNER,
                    event_type=PARTNER_SEARCH_RISK_UPDATE,
                    data={
                        "person_id": person.id,
                        "token": token,
                    },
                )
            return

        time_to_search = random.expovariate(rate)

        if time_to_boundary is not None and time_to_search >= time_to_boundary:
            self.calendar.schedule(
                time=self.current_time + time_to_boundary,
                priority=PRIORITY_PARTNER,
                event_type=PARTNER_SEARCH_RISK_UPDATE,
                data={
                    "person_id": person.id,
                    "token": token,
                },
            )
        else:
            self.calendar.schedule(
                time=self.current_time + time_to_search,
                priority=PRIORITY_PARTNER,
                event_type=PARTNER_SEARCH,
                data={
                    "person_id": person.id,
                    "token": token,
                },
            )

    def _process_partner_eligibility_event(self, data: dict):
        person = self._get_person_by_id(data["person_id"])

        if person is None:
            return

        if not person.alive:
            return

        if person.partner_search_token != data["token"]:
            return

        self._schedule_partner_search_or_eligibility(person)

    def _process_partner_search_risk_update_event(self, data: dict):
        person = self._get_person_by_id(data["person_id"])

        if person is None:
            return

        if not person.alive:
            return

        if person.partner_search_token != data["token"]:
            return

        self._schedule_partner_search_or_eligibility(person)

    def _process_partner_search_event(self, data: dict):
        person = self._get_person_by_id(data["person_id"])

        if person is None:
            return

        if person.partner_search_token != data["token"]:
            return

        if not self._can_search_partner(person):
            return

        candidate = self._find_partner_candidate(person)

        if candidate is not None:
            self._form_couple(person, candidate)
        else:
            self._schedule_partner_search_or_eligibility(person)

    def _can_search_partner(self, person: Person) -> bool:
        if not person.alive:
            return False

        if person.partner_id is not None:
            return False

        if not person.available_for_partner:
            return False

        if person.age(self.current_time) < 12:
            return False

        return True

    def _find_partner_candidate(self, person: Person):
        candidates = []

        for candidate in self.get_alive_people():
            if candidate.id == person.id:
                continue

            if candidate.sex == person.sex:
                continue

            if not self._can_search_partner(candidate):
                continue

            candidates.append(candidate)

        random.shuffle(candidates)

        for candidate in candidates:
            candidate_age = candidate.age(self.current_time)
            candidate_desire_probability = get_annual_partner_desire_probability(
                candidate_age
            )

            if not event_occurs(candidate_desire_probability):
                continue

            age_difference = abs(
                person.age(self.current_time) - candidate.age(self.current_time)
            )

            formation_probability = get_partner_formation_probability(age_difference)

            if event_occurs(formation_probability):
                return candidate

        return None

    def _form_couple(self, person_a: Person, person_b: Person):
        relationship_id = self.next_relationship_id
        self.next_relationship_id += 1

        person_a.partner_id = person_b.id
        person_b.partner_id = person_a.id

        person_a.relationship_id = relationship_id
        person_b.relationship_id = relationship_id

        person_a.partner_search_token += 1
        person_b.partner_search_token += 1

        self.counters.total_couples_created += 1

        self._schedule_breakup(person_a, person_b, relationship_id)

        if person_a.sex == "F":
            self._schedule_pregnancy_or_pregnancy_risk_update(person_a)
        else:
            self._schedule_pregnancy_or_pregnancy_risk_update(person_b)

    # -------------------------------------------------
    # Breakup and loneliness events
    # -------------------------------------------------

    def _schedule_breakup(
        self,
        person_a: Person,
        person_b: Person,
        relationship_id: int,
    ):
        annual_breakup_probability = 0.20
        rate = annual_probability_to_rate(annual_breakup_probability)

        time_to_breakup = random.expovariate(rate)

        self.calendar.schedule(
            time=self.current_time + time_to_breakup,
            priority=PRIORITY_BREAKUP,
            event_type=BREAKUP,
            data={
                "person_a_id": person_a.id,
                "person_b_id": person_b.id,
                "relationship_id": relationship_id,
            },
        )

    def _process_breakup_event(self, data: dict):
        person_a = self._get_person_by_id(data["person_a_id"])
        person_b = self._get_person_by_id(data["person_b_id"])

        if person_a is None or person_b is None:
            return

        if not person_a.alive or not person_b.alive:
            return

        relationship_id = data["relationship_id"]

        if person_a.relationship_id != relationship_id:
            return

        if person_b.relationship_id != relationship_id:
            return

        person_a.partner_id = None
        person_b.partner_id = None

        person_a.relationship_id = None
        person_b.relationship_id = None

        if not person_a.pregnant:
            person_a.pregnancy_token += 1

        if not person_b.pregnant:
            person_b.pregnancy_token += 1

        self.counters.total_breakups += 1

        self._start_loneliness_period(person_a)
        self._start_loneliness_period(person_b)

    def _start_loneliness_period(self, person: Person):
        if not person.alive:
            return

        age = person.age(self.current_time)
        mean_years = get_loneliness_mean_years(age)

        if mean_years <= 0:
            person.available_for_partner = True
            person.loneliness_end_time = None
            self._schedule_partner_search_or_eligibility(person)
            return

        person.available_for_partner = False
        person.partner_search_token += 1

        person.loneliness_token += 1
        token = person.loneliness_token

        loneliness_duration = random.expovariate(1 / mean_years)
        person.loneliness_end_time = self.current_time + loneliness_duration

        self.calendar.schedule(
            time=person.loneliness_end_time,
            priority=PRIORITY_PARTNER,
            event_type=END_LONELINESS,
            data={
                "person_id": person.id,
                "token": token,
            },
        )

    def _process_end_loneliness_event(self, data: dict):
        person = self._get_person_by_id(data["person_id"])

        if person is None:
            return

        if not person.alive:
            return

        if person.loneliness_token != data["token"]:
            return

        if person.partner_id is not None:
            return

        person.available_for_partner = True
        person.loneliness_end_time = None

        self._schedule_partner_search_or_eligibility(person)

    # -------------------------------------------------
    # Pregnancy and birth events
    # -------------------------------------------------

    def _schedule_pregnancy_or_pregnancy_risk_update(self, woman: Person):
        if not self._can_become_pregnant(woman):
            return

        woman.pregnancy_token += 1
        token = woman.pregnancy_token

        age = woman.age(self.current_time)

        annual_probability = get_annual_pregnancy_probability(age)
        rate = annual_probability_to_rate(annual_probability)

        next_boundary = get_next_pregnancy_age_boundary(age)

        if next_boundary is None:
            time_to_boundary = None
        else:
            time_to_boundary = next_boundary - age

        if rate <= 0:
            if time_to_boundary is not None:
                self.calendar.schedule(
                    time=self.current_time + time_to_boundary,
                    priority=PRIORITY_PREGNANCY,
                    event_type=PREGNANCY_RISK_UPDATE,
                    data={
                        "woman_id": woman.id,
                        "relationship_id": woman.relationship_id,
                        "token": token,
                    },
                )
            return

        time_to_pregnancy = random.expovariate(rate)

        if time_to_boundary is not None and time_to_pregnancy >= time_to_boundary:
            self.calendar.schedule(
                time=self.current_time + time_to_boundary,
                priority=PRIORITY_PREGNANCY,
                event_type=PREGNANCY_RISK_UPDATE,
                data={
                    "woman_id": woman.id,
                    "relationship_id": woman.relationship_id,
                    "token": token,
                },
            )
        else:
            self.calendar.schedule(
                time=self.current_time + time_to_pregnancy,
                priority=PRIORITY_PREGNANCY,
                event_type=PREGNANCY,
                data={
                    "woman_id": woman.id,
                    "relationship_id": woman.relationship_id,
                    "token": token,
                },
            )

    def _can_become_pregnant(self, woman: Person) -> bool:
        if not woman.alive:
            return False

        if woman.sex != "F":
            return False

        if woman.pregnant:
            return False

        if woman.partner_id is None:
            return False

        if woman.relationship_id is None:
            return False

        if woman.age(self.current_time) < 12:
            return False

        partner = self._get_person_by_id(woman.partner_id)

        if partner is None:
            return False

        if not partner.alive:
            return False

        max_allowed_children = min(
            woman.desired_children,
            partner.desired_children,
        )

        if woman.current_children >= max_allowed_children:
            return False

        return True

    def _process_pregnancy_risk_update_event(self, data: dict):
        woman = self._get_person_by_id(data["woman_id"])

        if woman is None:
            return

        if woman.pregnancy_token != data["token"]:
            return

        if woman.relationship_id != data["relationship_id"]:
            return

        self._schedule_pregnancy_or_pregnancy_risk_update(woman)

    def _process_pregnancy_event(self, data: dict):
        woman = self._get_person_by_id(data["woman_id"])

        if woman is None:
            return

        if woman.pregnancy_token != data["token"]:
            return

        if woman.relationship_id != data["relationship_id"]:
            return

        if not self._can_become_pregnant(woman):
            return

        father = self._get_person_by_id(woman.partner_id)

        if father is None:
            return

        woman.pregnant = True
        woman.pregnancy_father_id = father.id
        woman.childbirth_time = self.current_time + 0.75

        self.counters.total_pregnancies += 1

        woman.pregnancy_token += 1
        birth_token = woman.pregnancy_token

        self.calendar.schedule(
            time=woman.childbirth_time,
            priority=PRIORITY_BIRTH,
            event_type=BIRTH,
            data={
                "woman_id": woman.id,
                "father_id": father.id,
                "token": birth_token,
            },
        )

    def _process_birth_event(self, data: dict):
        woman = self._get_person_by_id(data["woman_id"])

        if woman is None:
            return

        if not woman.alive:
            return

        if woman.pregnancy_token != data["token"]:
            return

        if not woman.pregnant:
            return

        number_of_babies = generate_number_of_babies()

        for _ in range(number_of_babies):
            baby_sex = "M" if random.random() < 0.5 else "F"
            self._add_person(sex=baby_sex, age=0)
            self.counters.total_births += 1

        woman.current_children += number_of_babies

        father = self._get_person_by_id(data["father_id"])

        if father is not None and father.alive:
            father.current_children += number_of_babies

        woman.pregnant = False
        woman.childbirth_time = None
        woman.pregnancy_father_id = None

        self._schedule_pregnancy_or_pregnancy_risk_update(woman)

    # -------------------------------------------------
    # Statistics
    # -------------------------------------------------

    def _schedule_statistics_events(self):
        for year in range(1, self.years + 1):
            self.calendar.schedule(
                time=float(year),
                priority=PRIORITY_STATISTICS,
                event_type=COLLECT_STATISTICS,
                data={},
            )

    def _collect_yearly_statistics(self):
        statistics = collect_statistics(
            population=self.population,
            current_time=self.current_time,
            counters=self.counters,
        )

        self.yearly_statistics.append(statistics)