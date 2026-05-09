import random


def event_occurs(probability: float) -> bool:
    return random.random() < probability


def weighted_choice(options, weights):
    if len(options) != len(weights):
        raise ValueError("options and weights must have the same length")

    if not options:
        raise ValueError("options cannot be empty")

    total_weight = sum(weights)

    if total_weight <= 0:
        raise ValueError("total weight must be positive")

    random_value = random.uniform(0, total_weight)

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

    return random.uniform(epsilon, remaining)