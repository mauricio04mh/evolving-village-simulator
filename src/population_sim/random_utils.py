import math


LCG_MODULUS = 2_147_483_647
LCG_MULTIPLIER = 48_271
_lcg_state = 1


def seed_random_variable_generator(seed: int):
    global _lcg_state

    _lcg_state = int(seed) % LCG_MODULUS

    if _lcg_state == 0:
        _lcg_state = 1


def standard_uniform_open() -> float:
    """
    Generates U(0, 1) with a multiplicative congruential generator.

    This is the only primitive pseudo-random generator used by the project.
    The remaining variables are generated with the methods from the course:
    inverse transform for continuous variables and distribution inversion for
    discrete variables.
    """
    global _lcg_state

    _lcg_state = (LCG_MULTIPLIER * _lcg_state) % LCG_MODULUS
    return _lcg_state / LCG_MODULUS


def standard_uniform() -> float:
    return standard_uniform_open()


def uniform(lower: float, upper: float) -> float:
    """
    Generates U(lower, upper) by inverse transform:
    X = lower + (upper - lower) * U.
    """
    if upper < lower:
        raise ValueError("upper must be >= lower")

    return lower + (upper - lower) * standard_uniform()


def exponential(mean: float) -> float:
    """
    Generates an exponential variable by inverse transform:
    X = -mean * ln(U), where mean = 1 / lambda.
    """
    if mean <= 0:
        raise ValueError("mean must be > 0")

    return -mean * math.log(standard_uniform_open())


def event_occurs(probability: float) -> bool:
    if probability <= 0:
        return False

    if probability >= 1:
        return True

    return standard_uniform() < probability


def shuffle_in_place(values):
    """
    Generates a random permutation using the exchange algorithm described
    in the course notes.
    """
    for index in range(len(values) - 1, 0, -1):
        swap_index = int(standard_uniform() * (index + 1))
        values[index], values[swap_index] = values[swap_index], values[index]


def weighted_choice(options, weights):
    """
    Generates a finite discrete variable by inversion of the distribution
    function. Weights are normalized implicitly by their total sum.
    """
    if len(options) != len(weights):
        raise ValueError("options and weights must have the same length")

    if not options:
        raise ValueError("options cannot be empty")

    total_weight = sum(weights)

    if total_weight <= 0:
        raise ValueError("total weight must be positive")

    random_value = uniform(0, total_weight)

    cumulative_weight = 0

    for option, weight in zip(options, weights):
        cumulative_weight += weight

        if random_value <= cumulative_weight:
            return option

    return options[-1]


def remaining_interval_probability(
    interval_probability: float,
    interval_start: float,
    interval_end: float,
    current_age: float,
    conditional_on_survival: bool = True,
) -> float:
    """
    Computes the probability that an event occurs in the remaining part
    of an interval, assuming the event time is uniformly distributed
    inside the full interval if it occurs.

    Example:
        Full interval: [45, 76]
        P(event during full interval) = 0.30
        Current age = 60

    If conditional_on_survival=True, the function computes the probability
    of the event occurring after current_age, given that the person has
    already reached current_age without the event.
    """
    if interval_probability <= 0:
        return 0.0

    if interval_probability >= 1:
        return 1.0

    interval_length = interval_end - interval_start

    if interval_length <= 0:
        return 0.0

    if current_age >= interval_end:
        return 0.0

    if current_age < interval_start:
        current_age = interval_start

    elapsed = current_age - interval_start
    remaining = interval_end - current_age

    unconditional_remaining_probability = (
        interval_probability * remaining / interval_length
    )

    if not conditional_on_survival:
        return max(0.0, min(1.0, unconditional_remaining_probability))

    survival_to_current_probability = 1 - (
        interval_probability * elapsed / interval_length
    )

    if survival_to_current_probability <= 0:
        return 1.0

    conditional_probability = (
        unconditional_remaining_probability / survival_to_current_probability
    )

    return max(0.0, min(1.0, conditional_probability))


def sample_uniform_delay_until_interval_end(
    current_age: float,
    interval_end: float,
    epsilon: float,
) -> float:
    """
    Samples a delay uniformly between the current age and the end of the interval.

    The returned value is a delay in years, not an absolute age.
    """
    remaining = interval_end - current_age

    if remaining <= epsilon:
        return epsilon

    return uniform(epsilon, remaining)
