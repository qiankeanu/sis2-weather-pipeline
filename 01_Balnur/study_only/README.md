# SIS 2 — Kazakhstan Weather Data Pipeline

**API → real Apache Kafka → Pandera → pandas/NumPy → SQLite3 → EDA.**

Five cities: Almaty, Astana, Shymkent, Karaganda, Atyrau. Full year 2025:
5 × 365 = 1,825 daily API records. No API key is needed for this non-commercial project.
Data are ERA5 reanalysis estimates, not raw measurements from individual weather stations.
Source attribution: [Open-Meteo](https://open-meteo.com/) and ERA5 / Copernicus Climate Change Service.
Data licence: CC BY 4.0. Full API request URLs and grid coordinates are saved in
`results/collection.json`; untouched API responses are in `data/raw_responses/`.

## Quick start in VS Code

Open this **folder** in VS Code. Use Python 3.13 (the tested version), Java 17+ for
native Kafka, or Docker Desktop with Compose. Internet is needed only to install software
and fetch fresh API data; `--use-snapshot` reuses the preserved real API dataset.
Kafka is still required in snapshot mode.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
```

On Windows activate with `.venv\Scripts\activate` and use Docker for Kafka.
In VS Code select `.venv` through **Python: Select Interpreter** and select the same
environment as the notebook kernel. Python and Jupyter extensions are needed for notebooks.

### Start a real Kafka Broker — choose one method

Docker (configured broker/controller, loopback port 9092, automatic health check):

```bash
docker compose up -d --wait
```

Or macOS/Linux with Java 17+ (downloads official Kafka 3.9.1 and verifies SHA-512):

```bash
python scripts/start_kafka_local.py
```

Keep the native Kafka terminal open and use a second terminal for the next commands.
Never run both broker methods on port 9092 simultaneously. Local Kafka state and logs
are in `.runtime/`, excluded from Git. Docker setup is provided; the native broker path
is the one used for this project's recorded execution.

### Run the complete project

```bash
python main.py                 # fresh real API requests, all stages
python main.py --use-snapshot  # same saved real records, real Kafka again
python -m pytest -q
```

Expected default counts: collected = published = consumed = 1,825. Valid + invalid must
equal consumed. Cleaned = valid minus duplicate rows. Stored must equal cleaned.
Actual counts are in `results/pipeline_counts.csv` and `results/pipeline_verification.json`.
No invalid source data or execution results are fabricated. If real source data have no
errors, four isolated intentionally invalid examples demonstrate Pandera detection.

Consumer termination: it reads the expected number of messages for the current `run_id`
and verifies the whole dataset SHA-256. Old runs in the topic are ignored. Missing messages
cause an explicit timeout/error, not a fake success. One topic/partition is sufficient.

Default broker/topic are `127.0.0.1:9092` / `sis2-weather-daily`. Optional environment
variables: `KAFKA_BOOTSTRAP_SERVERS`, `KAFKA_TOPIC`. There are no credentials or private files.
The Producer creates the topic with one partition and replication factor 1 if absent.

### Execute individual stages in order

```bash
python -m src.api_client
python -m src.producer
python -m src.consumer
python -m src.validator
python -m src.cleaner
python -m src.loader
python -m src.analysis
python -m src.verification
```

Producer and Consumer are separate scripts; for this finite stream it is valid to publish
before starting the Consumer because Kafka retains the messages. Start from the project root
and use `python -m src...`, so imports work without hard-coded paths.

### Inspect database and results

```bash
sqlite3 data/weather.db < sql/verify.sql
```

SQLite is built into Python; the optional `sqlite3` CLI is not required by the pipeline.
`src.loader` executes SQL checks and stores `results/sql_city_summary.csv` itself.
It loads the same data twice, checks zero inserts on the second load, compares all stored
values with the cleaned dataset, and checks an unchanged database content hash.

`figures/` has five figures. `results/findings.md` explains every figure with actual values.
`results/descriptive_statistics.csv`, `weather_code_counts.csv`, `eda_city_summary.csv`,
and `monthly_temperature_pivot.csv` contain the supporting analyses.

For a different API period use `python main.py --start-date YYYY-MM-DD --end-date YYYY-MM-DD`.
Before switching periods, preserve/rename the old `data/weather.db`: the project deliberately
fails verification if a database contains unrelated old rows. For exact reproduction of the
included results, use `--use-snapshot`; a live reanalysis archive can be revised by its provider.

### Team and notebooks

See `TEAM.md` for the four named responsibilities and files to commit. Notebooks in
`notebooks/` explain and run the same source functions in small sections. They are internal
learning/handoff files: the assignment requires executable `.py` modules for submission.
Their source cells are generated from the modules by `scripts/build_notebooks.py` to prevent
two different implementations. Rebuild them after changing `.py` source files.

### Additional analysis

We compare frost days (minimum < 0°C), hot days (maximum ≥ 30°C), wet days (precipitation ≥ 1 mm),
hot/dry days (two conditions), and within-city monthly temperature deviations. These are
descriptive indicators, not official weather warnings or long-term climate anomalies.
There is no ML training requirement in SIS 2; evaluation here checks data quality, transport,
database correctness and reproducibility.

### Troubleshooting

- `NoBrokersAvailable`: start Kafka, wait for readiness, check port 9092 and broker address.
- API failure: inspect the error and retry later; use `--use-snapshot` to reproduce saved data.
- Schema errors: inspect `results/validation_errors.csv` and quarantined `data/invalid_data.csv`.
- Consumer timeout: check the broker and rerun Producer, then Consumer; use the same topic.
- Database mismatch: do not hide the failure. Preserve the old database and rerun for a fresh
  dataset, or investigate the difference. A repeated identical dataset requires no reset.

Stop Docker with `docker compose down`; stop native Kafka with Ctrl+C in its terminal.
No remote repository has been created and nothing is pushed automatically.

## Report and individual handoff

`report/project_report.pdf` is generated from the actual saved results. Group 7 and all
member names/student IDs are stored in `docs/team.json`. Confirm actual individual
contributions before submission. To rebuild after a pipeline change:

```bash
python -m pip install -r requirements-report.txt
python scripts/build_report.py --group YOUR_GROUP_NUMBER
python scripts/package_handoff.py
```

The four participant ZIPs and one full-project ZIP are in `handoff/`. The archives exclude
Python environments, Kafka binaries, broker data and caches. Source modules, real input
data, outputs, notebooks and documentation are included as appropriate for each part.

## Official references

- https://open-meteo.com/en/docs/historical-weather-api
- https://kafka.apache.org/39/quickstart/
- https://kafka-python.readthedocs.io/
- https://pandera.readthedocs.io/
- https://pandas.pydata.org/docs/
- https://numpy.org/doc/
- https://docs.python.org/3/library/sqlite3.html
- https://matplotlib.org/stable/
- https://seaborn.pydata.org/
