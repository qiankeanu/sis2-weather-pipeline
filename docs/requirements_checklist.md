# SIS 2 evidence checklist

| Requirement | Implementation | Reproducible evidence |
|---|---|---|
| Public API, ≥200 records, numeric/category/date fields | `src/api_client.py` | `data/raw_data.csv`, `data/raw_responses/`, `results/collection.json` |
| Error handling and raw preservation | retries/timeouts/HTTP checks, original JSON | API source code, request metadata |
| Real Kafka broker, topic, separate Producer/Consumer | native Kafka or Docker; `src/producer.py`, `src/consumer.py` | producer/consumer JSON, offsets, run_id, matching source/consumed hashes |
| At least five meaningful Pandera checks | schema in `src/validator.py` | field rules, validation summaries and error CSV |
| Deliberately invalid tests | four isolated mutations of real rows | `data/test_only/`, `results/validation_tests.json` |
| Missing values, duplicate removal, types, text normalization | `src/cleaner.py` | `results/cleaning.json`, `data/cleaned_data.csv` |
| NumPy operations | range, indicators, deviations | cleaned columns and source |
| Multi-condition filtering | hot and dry days | `data/hot_dry_days.csv` |
| GroupBy | city aggregation and monthly baseline | city summary CSV |
| Reshaping | `pivot_table` city × month | monthly pivot CSV, heatmap |
| SQLite schema, primary key, SQL checks | `src/loader.py`, `sql/` | database JSON and SQL city summary |
| Repeat loading without duplicates or value changes | two loads, row comparison, SHA-256 | first/second-load counts and hashes |
| EDA and ≥3 figures | `src/analysis.py`, five figures | descriptive/category stats, PNGs, `results/findings.md` |
| Connected stages and counts | `main.py`, `src/verification.py` | counts CSV and final verification JSON |
| Executable Python scripts | modules in `src/` | documented commands in README |
| Four individual responsibilities | `TEAM.md`, notebooks | source code, named learning/handoff packages |
| Project report | report generated from actual results | final PDF must match this exact repository version |
| Oral defence | `TEAM.md` preparation questions | all participants run and explain the complete pipeline |

No machine-learning model is needed. Pipeline evaluation verifies data and systems behaviour.
The source document also lists a topic/member registration deadline of 01.11.2026 and requires
different APIs per group; the team is responsible for instructor coordination.
