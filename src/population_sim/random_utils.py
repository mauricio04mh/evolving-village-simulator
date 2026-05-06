import math
import random


def event_occurs(probability: float) -> bool:
    return random.random() < probability


def interval_probability_to_rate(probability: float, interval_length: float) -> float:
    """
    Converts a probability associated with a complete interval into
    a continuous-time event rate.

    If P(event during interval of length L) = p, then:

        rate = -ln(1 - p) / L

    This rate can be used with an exponential distribution.
    """
    if probability <= 0:
        return 0.0

    if probability >= 1:
        return float("inf")

    if interval_length <= 0:
        return 0.0

    return -math.log(1 - probability) / interval_length


def annual_probability_to_rate(probability: float) -> float:
    """
    Converts an annual probability into a continuous-time yearly rate.

    This is still useful for events that are explicitly assumed to be annual,
    such as relationship breakups.
    """
    return interval_probability_to_rate(probability, 1.0)


def weighted_choice(options, weights):
    total_weight = sum(weights)
    random_value = random.uniform(0, total_weight)

    cumulative_weight = 0

    for option, weight in zip(options, weights):
        cumulative_weight += weight

        if random_value <= cumulative_weight:
            return option

    return options[-1]