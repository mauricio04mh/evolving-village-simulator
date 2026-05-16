import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from population_sim.experiments import run_experiments


def build_parser():
    parser = argparse.ArgumentParser(
        description="Run multiple independent population simulation replications."
    )
    parser.add_argument("--initial-women", type=int, default=300)
    parser.add_argument("--initial-men", type=int, default=300)
    parser.add_argument("--years", type=int, default=100)
    parser.add_argument("--runs", type=int, default=10)
    parser.add_argument("--base-seed", type=int, default=42)
    parser.add_argument("--output-dir", default="outputs/experiments")
    return parser


def main():
    args = build_parser().parse_args()
    results = run_experiments(
        initial_women=args.initial_women,
        initial_men=args.initial_men,
        years=args.years,
        runs=args.runs,
        base_seed=args.base_seed,
        output_dir=args.output_dir,
    )

    print("Experiments finished.")
    print(f"yearly_statistics.csv: {results['yearly_statistics_path']}")
    print(f"final_summaries.csv: {results['final_summaries_path']}")
    print(f"aggregate_final_metrics.csv: {results['aggregate_final_metrics_path']}")


if __name__ == "__main__":
    main()
