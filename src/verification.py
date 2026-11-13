"""Итоговая сверка всех этапов. Ошибки не скрываются за красивыми графиками."""
import pandas as pd

from src.common import read_json, save_json
from src.config import METRICS


def verify_pipeline():
    collection = read_json(METRICS / "collection.json")
    producer = read_json(METRICS / "producer.json")
    consumer = read_json(METRICS / "consumer.json")
    validation = read_json(METRICS / "validation.json")
    cleaning = read_json(METRICS / "cleaning.json")
    database = read_json(METRICS / "database.json")
    tests = read_json(METRICS / "validation_tests.json")
    stages = {"collected": collection["collected"], "published": producer["published"],
              "consumed": consumer["consumed"], "valid": validation["valid"],
              "invalid": validation["invalid"], "after_cleaning": cleaning["after"],
              "stored": database["stored"]}
    checks = {
        "at_least_200": stages["collected"] >= 200,
        "collection_publish_consume_counts": stages["collected"] == stages["published"] == stages["consumed"],
        "source_and_stream_content": collection["dataset_sha256"] == producer["dataset_sha256"] == consumer["dataset_sha256"],
        "same_run": len({item["run_id"] for item in [producer, consumer, validation, cleaning, database]}) == 1,
        "validation_accounted": stages["consumed"] == stages["valid"] + stages["invalid"],
        "cleaning_accounted": stages["valid"] - cleaning["duplicates_removed"] == stages["after_cleaning"],
        "database_count": stages["after_cleaning"] == stages["stored"],
        "database_exact_content": database["exact_data_match"],
        "database_idempotency": database["idempotent"] and database["second_load"]["inserted"] == 0,
        "no_database_duplicates": database["duplicate_city_dates"] == 0,
        "negative_validation_tests": tests["detected_invalid"] == 4 and tests["unexpectedly_accepted"] == 0,
        "no_remaining_missing": cleaning["missing_after"] == 0,
    }
    result = {"run_id": producer["run_id"], "counts": stages, "checks": checks,
              "all_passed": all(checks.values()),
              "count_explanation": "Invalid source rows are quarantined; duplicate valid rows are removed. "
              "Four intentionally invalid test rows are separate and never part of production counts."}
    save_json(METRICS / "pipeline_verification.json", result)
    pd.DataFrame(stages.items(), columns=["stage", "records"]).to_csv(METRICS / "pipeline_counts.csv", index=False)
    print(pd.DataFrame(stages.items(), columns=["stage", "records"]).to_string(index=False), flush=True)
    if not result["all_passed"]:
        raise AssertionError(f"Pipeline verification failed: {checks}")
    print(f"Evaluation: {len(checks)}/{len(checks)} checks passed", flush=True)
    return result


# CLI
if __name__ == "__main__":
    verify_pipeline()
