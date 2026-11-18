"""Часть 3 — Nurdaulet: Pandera и ошибочные тесты."""
import numbers

import numpy as np
import pandas as pd
import pandera.pandas as pa

from src.common import read_json, save_json
from src.config import CITIES, DATA, END_DATE, METRICS, RAW_COLUMNS, START_DATE, WMO_CODES


def numeric_column(low, high, nullable=False):
    # Не превращаем ошибочную строку в правильное число перед проверкой.
    is_number = lambda value: (isinstance(value, numbers.Real)
                               and not isinstance(value, (bool, np.bool_)) and np.isfinite(value))
    return pa.Column(nullable=nullable, checks=[
        pa.Check(lambda s: s.map(is_number), name="numeric_and_finite"),
        pa.Check(lambda s: pd.to_numeric(s, errors="coerce").between(low, high),
                 name=f"range_{low}_{high}"),
    ])


def build_schema(start_date=START_DATE, end_date=END_DATE):
    return pa.DataFrameSchema({
        "record_id": pa.Column(str, pa.Check.str_matches(r"^[a-z]+_\d{4}-\d{2}-\d{2}$")),
        "city": pa.Column(str, pa.Check.isin(list(CITIES))),
        "date": pa.Column(str, pa.Check(
            lambda s: pd.to_datetime(s, format="%Y-%m-%d", errors="coerce").between(
                pd.Timestamp(start_date), pd.Timestamp(end_date)), name="valid_date_in_period")),
        "temperature_min": numeric_column(-90, 65),
        "temperature_max": numeric_column(-90, 65),
        "temperature_mean": numeric_column(-90, 65, nullable=True),
        "precipitation_mm": numeric_column(0, 2000),
        "wind_max_kmh": numeric_column(0, 500),
        "weather_code": pa.Column(checks=[
            pa.Check(lambda s: s.map(lambda x: isinstance(x, numbers.Real)
                                     and not isinstance(x, (bool, np.bool_))), name="numeric_weather_code"),
            pa.Check.isin(WMO_CODES),
        ]),
    }, strict=True, checks=[
        pa.Check(lambda df: pd.to_numeric(df["temperature_min"], errors="coerce") <=
                 pd.to_numeric(df["temperature_max"], errors="coerce"), name="min_not_above_max"),
        pa.Check(lambda df: df["record_id"] == df["city"].str.lower() + "_" + df["date"],
                 name="identifier_matches_city_date"),
        pa.Check(lambda df: df["temperature_mean"].isna() | (
            pd.to_numeric(df["temperature_mean"], errors="coerce").ge(
                pd.to_numeric(df["temperature_min"], errors="coerce")) &
            pd.to_numeric(df["temperature_mean"], errors="coerce").le(
                pd.to_numeric(df["temperature_max"], errors="coerce"))), name="mean_between_min_max"),
    ])


def validate_records(frame, start_date=START_DATE, end_date=END_DATE):
    frame = frame.reset_index(drop=True).copy()
    if set(frame.columns) != set(RAW_COLUMNS):
        raise ValueError("Dataset columns do not match the required source schema")
    try:
        build_schema(start_date, end_date).validate(frame, lazy=True)
        failures = pd.DataFrame(columns=["schema_context", "column", "check",
                                         "check_number", "failure_case", "index"])
        bad_indices = []
    except pa.errors.SchemaErrors as error:
        failures = error.failure_cases.copy()
        # Отсутствующие колонки или ошибка типа целой колонки требуют исправить схему/вход.
        if failures["index"].isna().any():
            raise ValueError(f"Dataset-level schema error:\n{failures.to_string()}") from error
        bad_indices = sorted(set(failures["index"].astype(int)))
    invalid = frame.loc[bad_indices].copy()
    valid = frame.drop(index=bad_indices).copy()
    return valid.reset_index(drop=True), invalid, failures


def validation_demo(frame):
    """Ошибочные примеры хранятся отдельно и не попадают в рабочую базу."""
    if len(frame) < 4:
        raise ValueError("Need four real records for isolated negative tests")
    tests = frame.head(4).copy().reset_index(drop=True)
    tests.loc[0, "precipitation_mm"] = -5
    tests.loc[1, "date"] = "2025-02-30"
    tests.loc[2, "weather_code"] = 999
    tests.loc[3, "temperature_min"] = 60
    collection = read_json(METRICS / "collection.json")
    valid, invalid, failures = validate_records(tests, collection["start_date"], collection["end_date"])
    tests.to_csv(DATA / "test_only" / "deliberately_invalid.csv", index=False)
    failures.to_csv(DATA / "test_only" / "detected_errors.csv", index=False)
    result = {"test_records": 4, "detected_invalid": len(invalid),
              "unexpectedly_accepted": len(valid), "excluded_from_production": True,
              "cases": ["negative precipitation", "impossible date", "unknown WMO code",
                        "minimum temperature above maximum"]}
    save_json(METRICS / "validation_tests.json", result)
    if len(invalid) != 4 or len(valid) != 0:
        raise AssertionError("Pandera did not detect every intentionally invalid record")
    return result


def run_validation():
    frame = pd.DataFrame(read_json(DATA / "consumed_data.json"))
    collection = read_json(METRICS / "collection.json")
    valid, invalid, failures = validate_records(frame, collection["start_date"], collection["end_date"])
    valid.to_csv(DATA / "valid_data.csv", index=False)
    invalid.to_csv(DATA / "invalid_data.csv", index=False)
    failures.to_csv(METRICS / "validation_errors.csv", index=False)
    summary = {"run_id": read_json(METRICS / "consumer.json")["run_id"],
               "received": len(frame), "valid": len(valid), "invalid": len(invalid),
               "missing_before_validation": {key: int(value) for key, value in frame.isna().sum().items()}}
    save_json(METRICS / "validation.json", summary)
    validation_demo(frame)
    print(f"Pandera: valid={len(valid)}, invalid={len(invalid)}; negative tests=4/4", flush=True)
    return valid


# CLI
if __name__ == "__main__":
    run_validation()
