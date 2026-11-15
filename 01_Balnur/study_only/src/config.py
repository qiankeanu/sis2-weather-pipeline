"""Общие настройки. Здесь можно менять период и города."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
METRICS = ROOT / "results"
FIGURES = ROOT / "figures"
API_URL = "https://archive-api.open-meteo.com/v1/archive"
START_DATE = "2025-01-01"
END_DATE = "2025-12-31"
TIMEZONE = "Asia/Almaty"
BROKER = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "127.0.0.1:9092")
TOPIC = os.getenv("KAFKA_TOPIC", "sis2-weather-daily")
CITIES = {
    "Almaty": (43.24, 76.89),
    "Astana": (51.17, 71.43),
    "Shymkent": (42.32, 69.59),
    "Karaganda": (49.80, 73.10),
    "Atyrau": (47.12, 51.92),
}
API_FIELDS = {
    "temperature_2m_min": "temperature_min",
    "temperature_2m_max": "temperature_max",
    "temperature_2m_mean": "temperature_mean",
    "precipitation_sum": "precipitation_mm",
    "wind_speed_10m_max": "wind_max_kmh",
    "weather_code": "weather_code",
}
WMO_CODES = [0, 1, 2, 3, 45, 48, 51, 53, 55, 56, 57, 61, 63, 65,
             66, 67, 71, 73, 75, 77, 80, 81, 82, 85, 86, 95, 96, 99]
RAW_COLUMNS = ["record_id", "city", "date", *API_FIELDS.values()]


def make_dirs():
    for folder in [DATA, DATA / "raw_responses", DATA / "test_only", METRICS, FIGURES]:
        folder.mkdir(parents=True, exist_ok=True)
