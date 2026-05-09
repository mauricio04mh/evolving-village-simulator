from population_sim.random_utils import weighted_choice
from population_sim.constants import EPSILON


def generate_desired_children() -> int:
    """
    The original values are interpreted as relative weights because
    they do not sum to 1.

    The category 'more than 5' is represented as 6.
    """
    options = [1, 2, 3, 4, 5, 6]
    weights = [0.6, 0.75, 0.35, 0.2, 0.1, 0.05]

    return weighted_choice(options, weights)

    
def generate_number_of_babies() -> int:
    """
    The original values are interpreted as relative weights because
    they sum to 1.02 instead of exactly 1.
    """
    options = [1, 2, 3, 4, 5]
    weights = [0.7, 0.18, 0.08, 0.04, 0.02]

    return weighted_choice(options, weights)


def get_next_age_boundary(age: float, boundaries: list[float]):
    for boundary in boundaries:
        if age < boundary - EPSILON:
            return boundary

    return None


# -------------------------------------------------
# Death rules
# -------------------------------------------------

def get_next_death_age_boundary(age: float):
    return get_next_age_boundary(age, [12, 45, 76, 125])


def get_death_interval_info(age: float, sex: str):
    """
    Returns:
        probability over the whole age interval,
        interval start age,
        interval end age

    The probability is NOT annual. It is interpreted as the probability
    of death during the complete age interval.
    """
    if age < 12:
        return 0.25, 0, 12

    if age < 45:
        probability = 0.10 if sex == "M" else 0.15
        return probability, 12, 45

    if age < 76:
        probability = 0.30 if sex == "M" else 0.35
        return probability, 45, 76

    probability = 0.70 if sex == "M" else 0.65
    return probability, 76, 125


# -------------------------------------------------
# Partner desire rules
# -------------------------------------------------

def get_next_partner_desire_age_boundary(age: float):
    return get_next_age_boundary(age, [12, 15, 21, 35, 45, 60, 125])


def get_partner_desire_interval_info(age: float):
    """
    Returns:
        probability over the whole age interval,
        interval start age,
        interval end age

    This probability is interpreted as the probability that a single
    available person initiates a partner search during the age interval.
    """
    if age < 12:
        return 0.0, 0, 12

    if age < 15:
        return 0.60, 12, 15

    if age < 21:
        return 0.65, 15, 21

    if age < 35:
        return 0.80, 21, 35

    if age < 45:
        return 0.60, 35, 45

    if age < 60:
        return 0.50, 45, 60

    return 0.20, 60, 125


def get_partner_formation_probability(age_difference: float) -> float:
    """
    This is an instantaneous probability evaluated when two available
    people are considered as a possible couple.
    """
    if age_difference < 5:
        return 0.45

    if age_difference < 10:
        return 0.40

    if age_difference < 15:
        return 0.35

    if age_difference < 20:
        return 0.25

    return 0.15


# -------------------------------------------------
# Pregnancy rules
# -------------------------------------------------

def get_next_pregnancy_age_boundary(age: float):
    return get_next_age_boundary(age, [12, 15, 21, 35, 45, 60, 125])


def get_pregnancy_interval_info(age: float):
    """
    Returns:
        probability over the whole age interval,
        interval start age,
        interval end age

    This probability is interpreted as the probability of a pregnancy
    occurring during the age interval, while the woman satisfies the
    required conditions.
    """
    if age < 12:
        return 0.0, 0, 12

    if age < 15:
        return 0.20, 12, 15

    if age < 21:
        return 0.45, 15, 21

    if age < 35:
        return 0.80, 21, 35

    if age < 45:
        return 0.40, 35, 45

    if age < 60:
        return 0.20, 45, 60

    return 0.05, 60, 125


# -------------------------------------------------
# Loneliness rules
# -------------------------------------------------

def get_loneliness_mean_years(age: float) -> float:
    """
    Returns the mean loneliness period in years after breakup or widowhood.

    The table gives time values such as 3 months, 6 months, 1 year,
    2 years and 4 years. These are interpreted as the mean of an
    exponential distribution.
    """
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