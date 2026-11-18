"""Часть 3 — Nurdaulet: pandas и NumPy."""
import numpy as np
import pandas as pd

from src.common import read_json, save_json
from src.config import DATA, METRICS


def clean_data(frame):
    frame = frame.copy()
    before = len(frame)
    missing_before = {key: int(value) for key, value in frame.isna().sum().items()}
    duplicates = int(frame.duplicated(subset=["record_id"]).sum())
    frame = frame.drop_duplicates(subset=["record_id"]).copy()
    frame["city"] = frame["city"].str.strip().str.title()
    frame["date"] = pd.to_datetime(frame["date"], format="%Y-%m-%d", errors="raise")
    columns = ["temperature_min", "temperature_max", "temperature_mean",
               "precipitation_mm", "wind_max_kmh", "weather_code"]
    for column in columns:
        frame[column] = pd.to_numeric(frame[column], errors="raise")
    imputed = int(frame["temperature_mean"].isna().sum())
    # Для отсутствующей средней берём приближение (min + max) / 2 и отмечаем замену.
    frame["mean_was_imputed"] = frame["temperature_mean"].isna().astype(int)
    frame["temperature_mean"] = frame["temperature_mean"].fillna(
        (frame["temperature_min"] + frame["temperature_max"]) / 2)
    frame["weather_code"] = frame["weather_code"].astype(int)
    frame["temperature_range"] = np.subtract(frame["temperature_max"], frame["temperature_min"])
    frame["month"] = frame["date"].dt.month
    frame["season"] = np.select([frame["month"].isin([12, 1, 2]),
                                  frame["month"].isin([3, 4, 5]),
                                  frame["month"].isin([6, 7, 8])],
                                 ["Winter", "Spring", "Summer"], default="Autumn")
    frame["is_rainy"] = np.where(frame["precipitation_mm"] >= 1, 1, 0)
    frame["is_frost"] = np.where(frame["temperature_min"] < 0, 1, 0)
    frame["is_hot"] = np.where(frame["temperature_max"] >= 30, 1, 0)
    monthly_mean = frame.groupby(["city", "month"])["temperature_mean"].transform("mean")
    frame["temperature_anomaly"] = np.subtract(frame["temperature_mean"], monthly_mean)
    if frame.isna().any().any():
        raise ValueError("Unexpected missing values remain after cleaning")
    frame.to_csv(DATA / "cleaned_data.csv", index=False, date_format="%Y-%m-%d")
    # Фильтрация с несколькими условиями на настоящих данных.
    hot_dry = frame[(frame["temperature_max"] >= 30) & (frame["precipitation_mm"] < 1)]
    hot_dry.to_csv(DATA / "hot_dry_days.csv", index=False, date_format="%Y-%m-%d")
    grouped = frame.groupby("city").agg(days=("record_id", "count"),
        mean_temperature=("temperature_mean", "mean"), precipitation_mm=("precipitation_mm", "sum"),
        frost_days=("is_frost", "sum"), hot_days=("is_hot", "sum"), rainy_days=("is_rainy", "sum"))
    grouped.to_csv(METRICS / "city_summary.csv")
    pivot = frame.pivot_table(index="city", columns="month", values="temperature_mean", aggfunc="mean")
    pivot.to_csv(METRICS / "monthly_temperature_pivot.csv")
    save_json(METRICS / "cleaning.json", {
        "run_id": read_json(METRICS / "validation.json")["run_id"],
        "before": before, "duplicates_removed": duplicates, "mean_values_imputed": imputed,
        "after": len(frame), "hot_dry_days": len(hot_dry), "missing_before": missing_before,
        "missing_after": int(frame.isna().sum().sum()),
        "anomaly_definition": "Daily mean minus this city-month mean; not a long-term climate anomaly",
    })
    print(f"Cleaned: {len(frame)}; duplicates removed={duplicates}; imputed means={imputed}", flush=True)
    return frame


# CLI
if __name__ == "__main__":
    clean_data(pd.read_csv(DATA / "valid_data.csv"))
