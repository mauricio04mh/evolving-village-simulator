def collect_statistics(population, current_time, counters):
    alive_people = [person for person in population if person.alive]

    men = [person for person in alive_people if person.sex == "M"]
    women = [person for person in alive_people if person.sex == "F"]

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

    return {
        "year": int(current_time),
        "total_population": len(alive_people),
        "men": len(men),
        "women": len(women),
        "couples": len(relationship_ids),
        "pregnant_women": len(pregnant_women),
        "average_age": average_age,
        "total_births": counters.total_births,
        "total_deaths": counters.total_deaths,
        "total_pregnancies": counters.total_pregnancies,
        "total_couples_created": counters.total_couples_created,
        "total_breakups": counters.total_breakups,
    }