"""Часть 1 — Dauirkhankyzy Balnur, 23B031274: API и исходные данные."""
import argparse
import time
from datetime import datetime, timezone

import pandas as pd
import requests

from src.config import API_URL, API_FIELDS, CITIES, DATA, END_DATE, METRICS
from src.config import RAW_COLUMNS, START_DATE, TIMEZONE, make_dirs
from src.common import read_json, records_hash, save_json


def request_weather(session, params):
    """Три попытки помогают при временной ошибке API или сети."""
    for attempt in range(3):
        try:
            response = session.get(API_URL, params=params, timeout=(10, 60))
            response.raise_for_status()
            result = response.json()
            if result.get("error") or "daily" not in result:
                raise ValueError(f"Unexpected API response: {result}")
            return result, response.url
        except (requests.RequestException, ValueError) as error:
            if attempt == 2:
                raise RuntimeError(f"API request failed after 3 attempts: {error}") from error
            time.sleep(2 ** attempt)


def collect_data(start_date=START_DATE, end_date=END_DATE):
    make_dirs()
    dates = pd.date_range(start_date, end_date)
    if len(dates) == 0:
        raise ValueError("Start date must be before end date")
    all_records, sources = [], []
    with requests.Session() as session:
        for city, (latitude, longitude) in CITIES.items():
            params = {"latitude": latitude, "longitude": longitude,
                      "start_date": start_date, "end_date": end_date,
                      "daily": ",".join(API_FIELDS), "timezone": TIMEZONE,
                      "temperature_unit": "celsius", "wind_speed_unit": "kmh",
                      "precipitation_unit": "mm", "models": "era5"}
            response, url = request_weather(session, params)
            # Сохраняем полный ответ до преобразования в плоскую таблицу.
            save_json(DATA / "raw_responses" / f"{city.lower()}.json", response)
            daily = response["daily"]
            if daily.get("time") != dates.strftime("%Y-%m-%d").tolist():
                raise ValueError(f"Unexpected date coverage for {city}")
            if any(len(daily.get(field, [])) != len(dates) for field in API_FIELDS):
                raise ValueError(f"Inconsistent API arrays for {city}")
            for index, date in enumerate(daily["time"]):
                record = {"record_id": f"{city.lower()}_{date}", "city": city, "date": date}
                for api_name, column in API_FIELDS.items():
                    record[column] = daily[api_name][index]
                all_records.append(record)
            sources.append({"city": city, "request_url": url, "parameters": params,
                            "grid_latitude": response["latitude"],
                            "grid_longitude": response["longitude"], "records": len(dates)})
            print(f"Collected {city}: {len(dates)} records", flush=True)
    if len(all_records) < 200:
        raise ValueError("The assignment requires at least 200 API records")
    save_json(DATA / "raw_data.json", all_records)
    pd.DataFrame(all_records, columns=RAW_COLUMNS).to_csv(DATA / "raw_data.csv", index=False)
    summary = {"collected_at_utc": datetime.now(timezone.utc).isoformat(),
               "start_date": start_date, "end_date": end_date,
               "collected": len(all_records), "dataset_sha256": records_hash(all_records),
               "source": "Open-Meteo Historical Weather API, ERA5 reanalysis",
               "licence": "CC BY 4.0; credit Open-Meteo and ERA5/Copernicus",
               "sources": sources}
    save_json(METRICS / "collection.json", summary)
    return pd.DataFrame(all_records)


def load_snapshot():
    records = read_json(DATA / "raw_data.json")
    summary = read_json(METRICS / "collection.json")
    if records_hash(records) != summary["dataset_sha256"]:
        raise ValueError("Raw snapshot hash does not match its collection metadata")
    return pd.DataFrame(records)


# CLI: эти строки нужны для запуска отдельного .py-файла.
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--start-date", default=START_DATE)
    parser.add_argument("--end-date", default=END_DATE)
    args = parser.parse_args()
    print(collect_data(args.start_date, args.end_date).head().to_string(index=False))
