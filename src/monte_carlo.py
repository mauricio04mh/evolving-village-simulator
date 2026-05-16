import argparse
import math
import statistics
from collections import defaultdict

from population_sim.random_utils import seed_random_variable_generator
from population_sim.simulation import PopulationSimulation

BASE_METRICS = [
    "total_population",
    "men",
    "women",
    "couples",
    "pregnant_women",
    "average_age",
    "total_births",
    "total_deaths",
    "total_pregnancies",
    "total_couples_created",
    "total_breakups",
]

ADDITIONAL_METRICS = [
    "children",
    "adults",
    "elderly",
    "fertile_women",
    "sex_ratio",
    "birth_rate",
    "death_rate",
]

SUMMARY_METRICS = BASE_METRICS + ADDITIONAL_METRICS


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
            "stddev": 0.0,
            "min": 0.0,
            "max": 0.0,
            "p05": 0.0,
            "p25": 0.0,
            "median": 0.0,
            "p75": 0.0,
            "p95": 0.0,
            "ci95_low": 0.0,
            "ci95_high": 0.0,
        }

    sorted_values = sorted(float(value) for value in values)
    n = len(sorted_values)
    mean_value = statistics.fmean(sorted_values)

    if n > 1:
        stddev_value = statistics.stdev(sorted_values)
        ci_margin = 1.96 * (stddev_value / math.sqrt(n))
    else:
        stddev_value = 0.0
        ci_margin = 0.0

    return {
        "count": n,
        "mean": mean_value,
        "stddev": stddev_value,
        "min": sorted_values[0],
        "max": sorted_values[-1],
        "p05": percentile(sorted_values, 5),
        "p25": percentile(sorted_values, 25),
        "median": percentile(sorted_values, 50),
        "p75": percentile(sorted_values, 75),
        "p95": percentile(sorted_values, 95),
        "ci95_low": mean_value - ci_margin,
        "ci95_high": mean_value + ci_margin,
    }


def run_single_replication(replication, seed, initial_women, initial_men, years):
    seed_random_variable_generator(seed)

    simulation = PopulationSimulation(
        initial_women=initial_women,
        initial_men=initial_men,
        years=years,
        show_progress=False,
    )

    yearly_statistics = simulation.run()
    enriched_rows = []

    for row in yearly_statistics:
        row_with_metadata = dict(row)
        row_with_metadata["replication"] = replication
        row_with_metadata["seed"] = seed
        enriched_rows.append(row_with_metadata)

    return enriched_rows, simulation.get_death_age_range_audit_rows()


def aggregate_by_year_and_metric(raw_rows, metrics):
    values_by_year = defaultdict(lambda: defaultdict(list))

    for row in raw_rows:
        year = int(row["year"])

        for metric in metrics:
            if metric in row:
                values_by_year[year][metric].append(float(row[metric]))

    summary_rows = []

    for year in sorted(values_by_year.keys()):
        for metric in metrics:
            metric_values = values_by_year[year].get(metric, [])
            metric_summary = summarize_values(metric_values)

            summary_rows.append(
                {
                    "year": year,
                    "metric": metric,
                    "count": metric_summary["count"],
                    "mean": metric_summary["mean"],
                    "stddev": metric_summary["stddev"],
                    "min": metric_summary["min"],
                    "max": metric_summary["max"],
                    "p05": metric_summary["p05"],
                    "p25": metric_summary["p25"],
                    "median": metric_summary["median"],
                    "p75": metric_summary["p75"],
                    "p95": metric_summary["p95"],
                    "ci95_low": metric_summary["ci95_low"],
                    "ci95_high": metric_summary["ci95_high"],
                }
            )

    return summary_rows


def run_monte_carlo(replications, initial_women, initial_men, years, base_seed):
    if replications < 1:
        raise ValueError("replications must be >= 1")

    if years < 1:
        raise ValueError("years must be >= 1")

    if initial_women < 0 or initial_men < 0:
        raise ValueError("initial_women and initial_men must be >= 0")

    all_rows = []
    all_death_age_audit_rows = []

    progress_interval = max(1, replications // 10)

    for replication in range(replications):
        seed = base_seed + replication

        replication_rows, death_audit_rows = run_single_replication(
            replication=replication,
            seed=seed,
            initial_women=initial_women,
            initial_men=initial_men,
            years=years,
        )
        all_rows.extend(replication_rows)
        all_death_age_audit_rows.extend(death_audit_rows)

        if (
            replication == 0
            or (replication + 1) % progress_interval == 0
            or (replication + 1) == replications
        ):
            print(
                "[monte_carlo] "
                f"completed {replication + 1}/{replications} replications "
                f"(last_seed={seed})"
            )

    summary_rows = aggregate_by_year_and_metric(all_rows, SUMMARY_METRICS)
    death_age_audit_summary_rows = aggregate_death_age_range_rows(
        all_death_age_audit_rows
    )
    return all_rows, summary_rows, death_age_audit_summary_rows


def aggregate_death_age_range_rows(rows):
    aggregated = defaultdict(
        lambda: {
            "people_started_range": 0,
            "deaths_in_range": 0,
            "deaths_at_125": 0,
        }
    )

    for row in rows:
        key = (
            row["sex"],
            int(row["interval_start"]),
            int(row["interval_end"]),
        )
        aggregated[key]["people_started_range"] += int(row["people_started_range"])
        aggregated[key]["deaths_in_range"] += int(row["deaths_in_range"])
        aggregated[key]["deaths_at_125"] += int(row.get("deaths_at_125", 0))

    output_rows = []
    interval_order = [(0, 12), (12, 45), (45, 76), (76, 125)]

    for sex in ("F", "M"):
        for interval_start, interval_end in interval_order:
            key = (sex, interval_start, interval_end)
            people_started_range = aggregated[key]["people_started_range"]
            deaths_in_range = aggregated[key]["deaths_in_range"]
            deaths_at_125 = aggregated[key]["deaths_at_125"]

            if people_started_range > 0:
                death_percentage = (deaths_in_range / people_started_range) * 100.0
                death_at_125_percentage = (
                    deaths_at_125 / people_started_range
                ) * 100.0
            else:
                death_percentage = 0.0
                death_at_125_percentage = 0.0

            output_rows.append(
                {
                    "sex": sex,
                    "age_range": f"{interval_start}-{interval_end}",
                    "interval_start": interval_start,
                    "interval_end": interval_end,
                    "people_started_range": people_started_range,
                    "deaths_in_range": deaths_in_range,
                    "death_percentage": death_percentage,
                    "deaths_at_125": deaths_at_125,
                    "death_at_125_percentage": death_at_125_percentage,
                }
            )

    return output_rows


def build_summary_lookup(summary_rows):
    return {
        (int(row["year"]), row["metric"]): row
        for row in summary_rows
    }


def print_periodic_table(summary_rows, years, year_step):
    lookup = build_summary_lookup(summary_rows)

    print()
    print("Year | Mean Pop | 95% CI Pop | Mean Births | Mean Deaths | Mean Age")
    print("-" * 76)

    all_years = sorted({int(row["year"]) for row in summary_rows})

    for year in all_years:
        if year % year_step != 0 and year != years:
            continue

        pop = lookup.get((year, "total_population"), {})
        births = lookup.get((year, "total_births"), {})
        deaths = lookup.get((year, "total_deaths"), {})
        avg_age = lookup.get((year, "average_age"), {})

        mean_pop = float(pop.get("mean", 0.0))
        ci_low = float(pop.get("ci95_low", 0.0))
        ci_high = float(pop.get("ci95_high", 0.0))
        mean_births = float(births.get("mean", 0.0))
        mean_deaths = float(deaths.get("mean", 0.0))
        mean_age = float(avg_age.get("mean", 0.0))

        print(
            f"{year:4d} | "
            f"{mean_pop:8.2f} | "
            f"[{ci_low:8.2f}, {ci_high:8.2f}] | "
            f"{mean_births:11.2f} | "
            f"{mean_deaths:11.2f} | "
            f"{mean_age:8.2f}"
        )


def print_final_year_metrics_table(summary_rows, years):
    lookup = build_summary_lookup(summary_rows)

    print()
    print(
        "Metric                | Mean       | StdDev     | P05        | "
        "Median     | P95        | 95% CI"
    )
    print("-" * 108)

    for metric in SUMMARY_METRICS:
        row = lookup.get((years, metric), {})

        mean_value = float(row.get("mean", 0.0))
        stddev_value = float(row.get("stddev", 0.0))
        p05_value = float(row.get("p05", 0.0))
        median_value = float(row.get("median", 0.0))
        p95_value = float(row.get("p95", 0.0))
        ci_low = float(row.get("ci95_low", 0.0))
        ci_high = float(row.get("ci95_high", 0.0))

        print(
            f"{metric:21s} | "
            f"{mean_value:10.4f} | "
            f"{stddev_value:10.4f} | "
            f"{p05_value:10.4f} | "
            f"{median_value:10.4f} | "
            f"{p95_value:10.4f} | "
            f"[{ci_low:10.4f}, {ci_high:10.4f}]"
        )


def print_death_age_range_audit_table(rows):
    print()
    print("Death percentage by started age range and sex")
    print("-" * 64)
    print("Sex | Age Range | Started Range | Deaths | Death %")
    print("-" * 64)

    for row in rows:
        print(
            f"{row['sex']:3s} | "
            f"{row['age_range']:9s} | "
            f"{int(row['people_started_range']):13d} | "
            f"{int(row['deaths_in_range']):6d} | "
            f"{float(row['death_percentage']):7.2f}%"
        )

    print()
    print("Deaths at exact age 125 (separated from 76-125)")
    print("-" * 62)
    print("Sex | Started 76-125 | Deaths @125 | Death % @125")
    print("-" * 62)

    for row in rows:
        if int(row["interval_start"]) != 76 or int(row["interval_end"]) != 125:
            continue

        print(
            f"{row['sex']:3s} | "
            f"{int(row['people_started_range']):14d} | "
            f"{int(row.get('deaths_at_125', 0)):11d} | "
            f"{float(row.get('death_at_125_percentage', 0.0)):11.2f}%"
        )


def build_arg_parser():
    parser = argparse.ArgumentParser(
        description="Run Monte Carlo population simulation and print console tables."
    )

    parser.add_argument("--replications", type=int, default=500)
    parser.add_argument("--initial-women", type=int, default=300)
    parser.add_argument("--initial-men", type=int, default=300)
    parser.add_argument("--years", type=int, default=100)
    parser.add_argument("--base-seed", type=int, default=42)
    parser.add_argument(
        "--year-step",
        type=int,
        default=10,
        help="Print periodic summary every N years.",
    )

    return parser


def main():
    parser = build_arg_parser()
    args = parser.parse_args()

    if args.year_step < 1:
        raise ValueError("year_step must be >= 1")

    print("Running Monte Carlo simulation...")
    print(
        "Config: "
        f"replications={args.replications}, "
        f"initial_women={args.initial_women}, "
        f"initial_men={args.initial_men}, "
        f"years={args.years}, "
        f"base_seed={args.base_seed}, "
        f"year_step={args.year_step}"
    )

    _, summary_rows, death_age_audit_summary_rows = run_monte_carlo(
        replications=args.replications,
        initial_women=args.initial_women,
        initial_men=args.initial_men,
        years=args.years,
        base_seed=args.base_seed,
    )

    print_periodic_table(
        summary_rows=summary_rows,
        years=args.years,
        year_step=args.year_step,
    )
    print_final_year_metrics_table(summary_rows=summary_rows, years=args.years)
    print_death_age_range_audit_table(rows=death_age_audit_summary_rows)


if __name__ == "__main__":
    main()
