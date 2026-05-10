def collect_statistics(population, current_time, counters, alive_people=None):
    if alive_people is None:
        alive_people = [person for person in population if person.alive]

    men = [person for person in alive_people if person.sex == "M"]
    women = [person for person in alive_people if person.sex == "F"]
    children = [person for person in alive_people if person.age(current_time) < 18]
    adults = [
        person
        for person in alive_people
        if 18 <= person.age(current_time) < 60
    ]
    elderly = [person for person in alive_people if person.age(current_time) >= 60]
    fertile_women = [
        person
        for person in women
        if 12 <= person.age(current_time) <= 44
    ]

    relationship_ids = set()

    for person in alive_people:
        if person.relationship_id is not None:
            relationship_ids.add(person.relationship_id)

    pregnant_women = [
        person
        for person in alive_people
        if person.sex == "F" and person.pregnant
    ]

    if alive_people:
        average_age = sum(
            person.age(current_time) for person in alive_people
        ) / len(alive_people)
    else:
        average_age = 0

    total_population = len(alive_people)
    women_count = len(women)

    if women_count > 0:
        sex_ratio = len(men) / women_count
    else:
        sex_ratio = 0.0

    if total_population > 0:
        birth_rate = counters.total_births / total_population
        death_rate = counters.total_deaths / total_population
    else:
        birth_rate = 0.0
        death_rate = 0.0

    return {
        "year": int(current_time),
        "total_population": total_population,
        "men": len(men),
        "women": women_count,
        "children": len(children),
        "adults": len(adults),
        "elderly": len(elderly),
        "fertile_women": len(fertile_women),
        "sex_ratio": sex_ratio,
        "birth_rate": birth_rate,
        "death_rate": death_rate,
        "couples": len(relationship_ids),
        "pregnant_women": len(pregnant_women),
        "average_age": average_age,
        "total_births": counters.total_births,
        "total_deaths": counters.total_deaths,
        "total_pregnancies": counters.total_pregnancies,
        "total_couples_created": counters.total_couples_created,
        "total_breakups": counters.total_breakups,
    }
