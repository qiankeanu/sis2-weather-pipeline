"""Проверяем ошибки данных и повторную загрузку, а не рисуем результаты тестов."""
import sqlite3

import pandas as pd
import pytest

from src.loader import load_once
from src.validator import validate_records


@pytest.fixture
def source_row():
    return {"record_id": "almaty_2025-01-01", "city": "Almaty", "date": "2025-01-01",
            "temperature_min": -5.0, "temperature_max": 3.0, "temperature_mean": -1.0,
            "precipitation_mm": 0.0, "wind_max_kmh": 10.0, "weather_code": 3}


@pytest.mark.parametrize("field,value", [
    ("precipitation_mm", -1.0), ("date", "2025-02-30"), ("weather_code", 999),
    ("temperature_min", 40.0), ("city", "Unknown"), ("wind_max_kmh", "fast"),
    ("temperature_max", float("inf")), ("precipitation_mm", True),
    ("weather_code", True),
])
def test_invalid_values_are_quarantined(source_row, field, value):
    good = source_row.copy()
    bad = source_row.copy()
    bad[field] = value
    frame = pd.DataFrame([good, bad])
    valid, invalid, errors = validate_records(frame)
    assert len(valid) == 1
    assert len(invalid) == 1
    assert not errors.empty
    assert valid.iloc[0].to_dict() == good


def test_optional_missing_mean_is_accepted(source_row):
    source_row["temperature_mean"] = None
    valid, invalid, _ = validate_records(pd.DataFrame([source_row]))
    assert len(valid) == 1 and invalid.empty


def test_missing_column_fails_loudly(source_row):
    del source_row["date"]
    with pytest.raises(ValueError, match="columns"):
        validate_records(pd.DataFrame([source_row]))


def test_database_loading_is_idempotent_and_preserves_values(tmp_path, source_row):
    row = {**source_row, "mean_was_imputed": 0, "temperature_range": 8.0,
           "month": 1, "season": "Winter", "is_rainy": 0, "is_frost": 1,
           "is_hot": 0, "temperature_anomaly": 0.0}
    frame = pd.DataFrame([row])
    database = tmp_path / "test.db"
    first = load_once(frame, database)
    second = load_once(frame, database)
    assert first["inserted"] == 1 and second["inserted"] == 0
    assert first["sha256"] == second["sha256"]
    with sqlite3.connect(database) as connection:
        assert connection.execute("SELECT precipitation_mm FROM weather_daily").fetchone() == (0.0,)
        # Новая плохая строка не должна молча игнорироваться SQLite.
        row["record_id"] = "almaty_2025-01-02"
        row["date"] = "2025-01-02"
        row["precipitation_mm"] = -5
        with pytest.raises(sqlite3.IntegrityError):
            load_once(pd.DataFrame([row]), database)


def test_cleaning_handles_missing_mean_and_duplicates(tmp_path, monkeypatch, source_row):
    from src import cleaner
    from src.common import save_json, read_json
    data = tmp_path / "data"
    results = tmp_path / "results"
    data.mkdir()
    results.mkdir()
    monkeypatch.setattr(cleaner, "DATA", data)
    monkeypatch.setattr(cleaner, "METRICS", results)
    save_json(results / "validation.json", {"run_id": "isolated-unit-test"})
    source_row["temperature_mean"] = None
    cleaned = cleaner.clean_data(pd.DataFrame([source_row, source_row.copy()]))
    assert len(cleaned) == 1
    assert cleaned.iloc[0]["temperature_mean"] == -1.0
    assert cleaned.iloc[0]["mean_was_imputed"] == 1
    assert cleaned.iloc[0]["temperature_range"] == 8.0
    assert cleaned.isna().sum().sum() == 0
    summary = read_json(results / "cleaning.json")
    assert summary["duplicates_removed"] == 1
    assert summary["mean_values_imputed"] == 1
