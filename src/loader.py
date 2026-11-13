"""Часть 4 — Kian: SQLite и идемпотентность."""
import hashlib
import sqlite3

import pandas as pd

from src.common import read_json, save_json
from src.config import DATA, METRICS, ROOT

DB_COLUMNS = ["record_id", "city", "date", "temperature_min", "temperature_max",
              "temperature_mean", "precipitation_mm", "wind_max_kmh", "weather_code",
              "mean_was_imputed", "temperature_range", "month", "season", "is_rainy",
              "is_frost", "is_hot", "temperature_anomaly"]


def database_digest(connection):
    rows = connection.execute("SELECT * FROM weather_daily ORDER BY record_id").fetchall()
    return hashlib.sha256(repr(rows).encode("utf-8")).hexdigest()


def load_once(frame, db_path):
    with sqlite3.connect(db_path) as connection:
        connection.executescript((ROOT / "sql" / "schema.sql").read_text(encoding="utf-8"))
        values = frame[DB_COLUMNS].copy()
        values["date"] = pd.to_datetime(values["date"]).dt.strftime("%Y-%m-%d")
        before = connection.total_changes
        placeholders = ",".join(["?"] * len(DB_COLUMNS))
        # Игнорируем только конфликт первичного ключа, а не ошибки CHECK/NOT NULL.
        statement = (f"INSERT INTO weather_daily ({','.join(DB_COLUMNS)}) VALUES ({placeholders}) "
                     "ON CONFLICT(record_id) DO NOTHING")
        connection.executemany(statement, values.itertuples(index=False, name=None))
        inserted = connection.total_changes - before
        return {"inserted": inserted, "stored": connection.execute(
            "SELECT COUNT(*) FROM weather_daily").fetchone()[0], "sha256": database_digest(connection)}


def run_loading(frame=None):
    if frame is None:
        frame = pd.read_csv(DATA / "cleaned_data.csv")
    db_path = DATA / "weather.db"
    first = load_once(frame, db_path)
    second = load_once(frame, db_path)
    if second["inserted"] != 0 or first["sha256"] != second["sha256"]:
        raise AssertionError("Repeated database loading changed the stored data")
    with sqlite3.connect(db_path) as connection:
        stored = pd.read_sql_query("SELECT * FROM weather_daily ORDER BY record_id", connection)
        # Сравниваем все значения, а не только размер таблицы.
        expected = frame[DB_COLUMNS].copy()
        expected["date"] = pd.to_datetime(expected["date"]).dt.strftime("%Y-%m-%d")
        expected = expected.sort_values("record_id").reset_index(drop=True)
        pd.testing.assert_frame_equal(expected, stored[DB_COLUMNS], check_dtype=False)
        duplicates = connection.execute("SELECT COUNT(*) FROM (SELECT city,date,COUNT(*) n "
                                        "FROM weather_daily GROUP BY city,date HAVING n > 1)").fetchone()[0]
        pd.read_sql_query("SELECT city, COUNT(*) AS records, AVG(temperature_mean) AS avg_temperature, "
                         "SUM(precipitation_mm) AS total_precipitation FROM weather_daily "
                         "GROUP BY city ORDER BY city", connection).to_csv(
                             METRICS / "sql_city_summary.csv", index=False)
    summary = {"run_id": read_json(METRICS / "cleaning.json")["run_id"],
               "processed": len(frame), "stored": len(stored), "first_load": first,
               "second_load": second, "duplicate_city_dates": duplicates,
               "exact_data_match": True, "idempotent": True}
    save_json(METRICS / "database.json", summary)
    print(f"SQLite: {len(stored)} records; second load inserted {second['inserted']}", flush=True)
    return summary


# CLI
if __name__ == "__main__":
    run_loading()
