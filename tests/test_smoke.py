import csv
import math
import random
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from population_sim.experiments import run_experiments
from population_sim.simulation import PopulationSimulation


class PopulationSimulationSmokeTest(unittest.TestCase):
    def test_yearly_statistics_have_expected_length_for_100_years(self):
        random.seed(123)
        simulation = PopulationSimulation(
            initial_women=2,
            initial_men=2,
            years=100,
            show_progress=False,
        )

        yearly_statistics = simulation.run()

        self.assertEqual(100, len(yearly_statistics))

    def test_final_summary_and_csv_outputs(self):
        random.seed(456)
        simulation = PopulationSimulation(
            initial_women=3,
            initial_men=3,
            years=12,
            show_progress=False,
        )

        yearly_statistics = simulation.run()
        final_summary = simulation.get_final_summary()

        expected_summary_keys = {
            "initial_women",
            "initial_men",
            "initial_population",
            "years",
            "final_population",
            "final_men",
            "final_women",
            "final_couples",
            "final_pregnant_women",
            "final_average_age",
            "total_births",
            "total_deaths",
            "total_pregnancies",
            "total_couples_created",
            "total_breakups",
            "total_widowhoods",
            "total_birth_events",
            "births_male",
            "births_female",
            "pregnancies_cancelled_by_maternal_death",
            "absolute_population_change",
            "relative_population_change",
            "extinction",
            "survival_population_ratio",
            "births_per_initial_person",
            "deaths_per_initial_person",
            "pregnancies_per_initial_woman",
            "births_per_pregnancy",
            "births_per_birth_event",
            "breakups_per_couple_created",
            "final_sex_ratio",
            "final_couple_ratio",
            "processed_events",
            "max_calendar_size",
            "final_calendar_size",
            "average_relationship_duration",
            "average_loneliness_duration",
        }

        self.assertTrue(expected_summary_keys.issubset(final_summary.keys()))

        for row in yearly_statistics:
            for metric in (
                "sex_ratio",
                "couple_ratio",
                "pregnancy_ratio",
                "birth_rate",
                "death_rate",
                "growth_rate",
                "births_per_pregnancy",
                "births_per_birth_event",
                "adult_couple_ratio",
            ):
                self.assertTrue(math.isfinite(float(row[metric])))

        self.assertEqual(
            final_summary["total_births"],
            final_summary["births_male"] + final_summary["births_female"],
        )
        self.assertLessEqual(
            final_summary["total_birth_events"],
            final_summary["total_births"],
        )
        self.assertEqual(
            final_summary["final_population"],
            final_summary["final_men"] + final_summary["final_women"],
        )
        self.assertLessEqual(
            final_summary["final_couples"],
            final_summary["final_population"] / 2,
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            results = run_experiments(
                initial_women=2,
                initial_men=2,
                years=5,
                runs=2,
                base_seed=900,
                output_dir=tmp_dir,
            )

            yearly_path = Path(results["yearly_statistics_path"])
            final_path = Path(results["final_summaries_path"])
            aggregate_path = Path(results["aggregate_final_metrics_path"])

            self.assertTrue(yearly_path.exists())
            self.assertTrue(final_path.exists())
            self.assertTrue(aggregate_path.exists())

            with yearly_path.open("r", newline="", encoding="utf-8") as handle:
                yearly_rows = list(csv.DictReader(handle))

            with final_path.open("r", newline="", encoding="utf-8") as handle:
                final_rows = list(csv.DictReader(handle))

            with aggregate_path.open("r", newline="", encoding="utf-8") as handle:
                aggregate_rows = list(csv.DictReader(handle))

            self.assertEqual(10, len(yearly_rows))
            self.assertEqual(2, len(final_rows))
            self.assertGreater(len(aggregate_rows), 0)


if __name__ == "__main__":
    unittest.main()
