import csv
import math
import random
import statistics
from pathlib import Path

from population_sim.simulation import PopulationSimulation


FINAL_SUMMARY_AGGREGATE_METRICS = [
    "final_population",
    "relative_population_change",
    "total_births",
    "total_deaths",
    "total_pregnancies",
    "total_couples_created",
    "total_breakups",
    "total_widowhoods",
    "final_average_age",
    "final_sex_ratio",
    "final_couple_ratio",
    "births_per_pregnancy",
    "births_per_birth_event",
    "breakups_per_couple_created",
    "average_relationship_duration",
    "average_loneliness_duration",
    "processed_events",
    "max_calendar_size",
]


def percentile(values, p):
    if not values:
        return 0.0

    if p <= 0:
        return values[0]

    if p >= 100:
        return values[-1]

    rank = (len(values) - 1) * (p / 100.0)
    lower_index = int(math.floor(rank))
    upper_index = int(math.ceil(rank))

    if lower_index == upper_index:
        return values[lower_index]

    fraction = rank - lower_index
    lower_value = values[lower_index]
    upper_value = values[upper_index]
    return lower_value + fraction * (upper_value - lower_value)


def summarize_values(values):
    if not values:
        return {
            "count": 0,
            "mean": 0.0,
            "std": 0.0,
            "min": 0.0,
            "max": 0.0,
            "median": 0.0,
            "p05": 0.0,
            "p25": 0.0,
            "p75": 0.0,
            "p95": 0.0,
            "ci95_low": 0.0,
            "ci95_high": 0.0,
        }

    sorted_values = sorted(float(value) for value in values)
    count = len(sorted_values)
    mean_value = statistics.fmean(sorted_values)

    if count > 1:
        std_value = statistics.stdev(sorted_values)
        ci_margin = 1.96 * std_value / math.sqrt(count)
    else:
        std_value = 0.0
        ci_margin = 0.0

    return {
        "count": count,
        "mean": mean_value,
        "std": std_value,
        "min": sorted_values[0],
        "max": sorted_values[-1],
        "median": percentile(sorted_values, 50),
        "p05": percentile(sorted_values, 5),
        "p25": percentile(sorted_values, 25),
        "p75": percentile(sorted_values, 75),
        "p95": percentile(sorted_values, 95),
        "ci95_low": mean_value - ci_margin,
        "ci95_high": mean_value + ci_margin,
    }


def write_csv_rows(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    rows = list(rows)
    if not rows:
        with path.open("w", newline="", encoding="utf-8") as handle:
            handle.write("")
        return path

    fieldnames = list(rows[0].keys())

    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return path


def aggregate_final_summaries(
    summaries,
    metrics=None,
):
    metrics = metrics or FINAL_SUMMARY_AGGREGATE_METRICS
    summary_rows = []

    for metric in metrics:
        values = []

        for row in summaries:
            if metric not in row:
                continue

            values.append(float(row[metric]))

        metric_summary = summarize_values(values)
        summary_rows.append({"metric": metric, **metric_summary})

    return summary_rows


def aggregate_final_summaries_csv(csv_path, metrics=None):
    with Path(csv_path).open("r", newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    return aggregate_final_summaries(rows, metrics=metrics)


def run_experiments(
    initial_women,
    initial_men,
    years,
    runs,
    base_seed,
    output_dir,
):
    if runs < 1:
        raise ValueError("runs must be >= 1")

    if years < 1:
        raise ValueError("years must be >= 1")

    if initial_women < 0 or initial_men < 0:
        raise ValueError("initial_women and initial_men must be >= 0")

    yearly_rows = []
    final_summary_rows = []

    for run_id in range(runs):
        seed = base_seed + run_id
        random.seed(seed)

        simulation = PopulationSimulation(
            initial_women=initial_women,
            initial_men=initial_men,
            years=years,
            show_progress=False,
        )

        yearly_statistics = simulation.run()
        final_summary = simulation.get_final_summary()

        for row in yearly_statistics:
            yearly_rows.append(
                {
                    "run_id": run_id,
                    "seed": seed,
                    **row,
                }
            )

        final_summary_rows.append(
            {
                "run_id": run_id,
                "seed": seed,
                **final_summary,
            }
        )

    aggregate_rows = aggregate_final_summaries(final_summary_rows)
    output_dir = Path(output_dir)

    yearly_path = write_csv_rows(output_dir / "yearly_statistics.csv", yearly_rows)
    final_path = write_csv_rows(output_dir / "final_summaries.csv", final_summary_rows)
    aggregate_path = write_csv_rows(
        output_dir / "aggregate_final_metrics.csv",
        aggregate_rows,
    )

    return {
        "yearly_statistics_path": str(yearly_path),
        "final_summaries_path": str(final_path),
        "aggregate_final_metrics_path": str(aggregate_path),
        "yearly_rows": yearly_rows,
        "final_summary_rows": final_summary_rows,
        "aggregate_rows": aggregate_rows,
    }
