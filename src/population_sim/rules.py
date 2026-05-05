from population_sim.random_utils import weighted_choice


def generate_desired_children() -> int:
    """
    The original values are interpreted as relative weights.
    The category 'more than 5' is represented as 6.
    """
    options = [1, 2, 3, 4, 5, 6]
    weights = [0.6, 0.75, 0.35, 0.2, 0.1, 0.05]

    return weighted_choice(options, weights)


def generate_number_of_babies() -> int:
    """
    The original probabilities sum to 1.02, so they are treated as weights.
    """
    options = [1, 2, 3, 4, 5]
    weights = [0.7, 0.18, 0.08, 0.04, 0.02]

    return weighted_choice(options, weights)


def get_next_age_boundary(age: float, boundaries: list[float]):
    for boundary in boundaries:
        if age < boundary:
            return boundary

    return None


def get_next_death_age_boundary(age: float):
    return get_next_age_boundary(age, [12, 45, 76])


def get_next_partner_desire_age_boundary(age: float):
    return get_next_age_boundary(age, [12, 15, 21, 35, 45, 60])


def get_next_pregnancy_age_boundary(age: float):
    return get_next_age_boundary(age, [12, 15, 21, 35, 45, 60])


def get_annual_death_probability(age: float, sex: str) -> float:
    if age < 12:
        return 0.25

    if age < 45:
        return 0.10 if sex == "M" else 0.15

    if age < 76:
        return 0.30 if sex == "M" else 0.35

    return 0.70 if sex == "M" else 0.65


def get_annual_partner_desire_probability(age: float) -> float:
    if age < 12:
        return 0.0

    if age < 15:
        return 0.60

    if age < 21:
        return 0.65

    if age < 35:
        return 0.80

    if age < 45:
        return 0.60

    if age < 60:
        return 0.50

    return 0.20


def get_partner_formation_probability(age_difference: float) -> float:
    if age_difference < 5:
        return 0.45

    if age_difference < 10:
        return 0.40

    if age_difference < 15:
        return 0.35

    if age_difference < 20:
        return 0.25

    return 0.15


def get_annual_pregnancy_probability(age: float) -> float:
    if age < 12:
        return 0.0

    if age < 15:
        return 0.20

    if age < 21:
        return 0.45

    if age < 35:
        return 0.80

    if age < 45:
        return 0.40

    if age < 60:
        return 0.20

    return 0.05


def get_loneliness_mean_years(age: float) -> float:
    if age < 12:
        return 0.0

    if age < 15:
        return 3 / 12

    if age < 21:
        return 6 / 12

    if age < 35:
        return 6 / 12

    if age < 45:
        return 1.0

    if age < 60:
        return 2.0

    return 4.0