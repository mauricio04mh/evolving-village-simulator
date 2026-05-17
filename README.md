# Evolving Village Simulator

Simulador de poblacion para una aldea, basado en eventos discretos. El modelo
representa nacimientos, muertes, formacion y ruptura de parejas, embarazos,
periodos de soledad y estadisticas anuales de la poblacion.

El repositorio incluye:

- `src/population_sim/`: paquete principal de la simulacion.
- `src/main.py`: ejecucion simple con una configuracion fija.
- `scripts/run_experiments.py`: ejecucion de varias replicas y exportacion a CSV.
- `src/monte_carlo.py`: corrida Monte Carlo con tablas resumen en consola.
- `tests/`: pruebas de humo del modelo y de la generacion de CSV.
- `report.pdf`: reporte final del proyecto.

## Requisitos

- Python 3.10 o superior recomendado.
- No se requieren dependencias externas; el proyecto usa la biblioteca estandar.

## Ejecutar una simulacion simple

Desde la raiz del repositorio:

```bash
python3 src/main.py
```

Esta ejecucion usa una semilla fija, una poblacion inicial de 500 mujeres y 500
hombres, y simula 100 anos. Al finalizar imprime una tabla con estadisticas cada
10 anos.

## Ejecutar experimentos y generar CSV

```bash
python3 scripts/run_experiments.py
```

Por defecto ejecuta 10 replicas de 100 anos con 300 mujeres y 300 hombres
iniciales. Los resultados se escriben en `outputs/experiments/`:

- `yearly_statistics.csv`: estadisticas anuales de cada replica.
- `final_summaries.csv`: resumen final de cada replica.
- `aggregate_final_metrics.csv`: agregados estadisticos de las metricas finales.

Tambien se pueden ajustar los parametros:

```bash
python3 scripts/run_experiments.py \
  --initial-women 300 \
  --initial-men 300 \
  --years 100 \
  --runs 30 \
  --base-seed 42 \
  --output-dir outputs/experiments
```

## Ejecutar Monte Carlo por consola

```bash
PYTHONPATH=src python3 src/monte_carlo.py
```

Este comando imprime tablas resumen de las replicas, intervalos de confianza y
auditoria de muertes por rango de edad. Los parametros principales son:

```bash
PYTHONPATH=src python3 src/monte_carlo.py \
  --replications 500 \
  --initial-women 300 \
  --initial-men 300 \
  --years 100 \
  --base-seed 42 \
  --year-step 10
```

## Correr las pruebas

```bash
python3 -m unittest discover -s tests
```

Las pruebas verifican que la generacion aleatoria este centralizada, que la
simulacion produzca estadisticas anuales y que los experimentos generen los CSV
esperados.

## Estructura general del modelo

La clase `PopulationSimulation` en `src/population_sim/simulation.py` coordina el
calendario de eventos y el estado de la poblacion. Las reglas probabilisticas
principales estan en `src/population_sim/rules.py`, mientras que la recoleccion
de metricas anuales esta en `src/population_sim/statistics.py`.

Para obtener resultados reproducibles, las ejecuciones fijan la semilla usando
`seed_random_variable_generator`.
