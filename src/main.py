import random

from population_sim.simulation import PopulationSimulation


def main():
    random.seed(42)

    initial_women = 150
    initial_men = 100
    years = 100

    simulation = PopulationSimulation(
        initial_women=initial_women,
        initial_men=initial_men,
        years=years,
    )

    results = simulation.run()

    print("Simulation finished.")
    print()
    print(
        "Year | Population | Men | Women | Couples | Pregnant | "
        "Avg Age | Births | Deaths | Pregnancies | Breakups"
    )
    print("-" * 115)

    for row in results:
        if row["year"] % 10 == 0 or row["year"] == years:
            print(
                f'{row["year"]:4d} | '
                f'{row["total_population"]:10d} | '
                f'{row["men"]:3d} | '
                f'{row["women"]:5d} | '
                f'{row["couples"]:7d} | '
                f'{row["pregnant_women"]:8d} | '
                f'{row["average_age"]:7.2f} | '
                f'{row["total_births"]:6d} | '
                f'{row["total_deaths"]:6d} | '
                f'{row["total_pregnancies"]:11d} | '
                f'{row["total_breakups"]:8d}'
            )


if __name__ == "__main__":
    main()