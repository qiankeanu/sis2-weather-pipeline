# SIS 2 team

Group: **7**.

Project: Weather Data Streaming and Validation Pipeline for Five Cities in Kazakhstan.
Period: 1 January–31 December 2025. Source: Open-Meteo Historical Weather API / ERA5.

| Member | Responsibility | Main source files |
|---|---|---|
| Balnur | API requests, HTTP error handling, original JSON/CSV and source metadata | `src/api_client.py`, `docs/data_dictionary.md` |
| Kundyz | Kafka broker, topic, JSON Producer and Consumer, message counts and content verification | `src/producer.py`, `src/consumer.py`, `scripts/start_kafka_local.py`, `docker-compose.yml` |
| Nurdaulet | Pandera validation, isolated invalid examples, pandas/NumPy cleaning, filtering, GroupBy and pivot | `src/validator.py`, `src/cleaner.py` |
| Kian | SQLite, SQL checks, repeated loading, EDA, pipeline evaluation and integration | `src/loader.py`, `src/analysis.py`, `src/verification.py`, `main.py`, `sql/`, `tests/` |

Shared configuration and file helpers are in `src/config.py` and `src/common.py`.
Each member is responsible for understanding their component and its place in the complete pipeline.
