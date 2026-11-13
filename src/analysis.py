"""Часть 4 — Kian: EDA, графики и выводы."""
import sqlite3

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from src.common import save_json
from src.config import CITIES, DATA, FIGURES, METRICS, make_dirs


def finish_plot(filename):
    plt.tight_layout()
    plt.savefig(FIGURES / filename, dpi=170, bbox_inches="tight")
    plt.close()


def run_analysis():
    make_dirs()
    with sqlite3.connect(DATA / "weather.db") as connection:
        frame = pd.read_sql_query("SELECT * FROM weather_daily ORDER BY date,city", connection,
                                  parse_dates=["date"])
    if frame.empty:
        raise ValueError("Database contains no weather data")
    frame.describe().to_csv(METRICS / "descriptive_statistics.csv")
    frame["weather_code"].value_counts().rename_axis("weather_code").to_csv(
        METRICS / "weather_code_counts.csv", header=["days"])
    summary = frame.groupby("city").agg(days=("record_id", "count"),
        mean_temperature=("temperature_mean", "mean"), precipitation_mm=("precipitation_mm", "sum"),
        frost_days=("is_frost", "sum"), hot_days=("is_hot", "sum"), rainy_days=("is_rainy", "sum"))
    summary.to_csv(METRICS / "eda_city_summary.csv")
    first_day, last_day = frame["date"].min(), frame["date"].max()
    period = str(first_day.year) if (first_day.strftime("%m-%d") == "01-01" and
        last_day.strftime("%m-%d") == "12-31" and first_day.year == last_day.year) else (
        f"{first_day:%Y-%m-%d} to {last_day:%Y-%m-%d}")
    sns.set_theme(style="whitegrid", palette="colorblind")
    order = list(CITIES)
    plt.figure(figsize=(11, 5))
    for city in order:
        city_data = frame[frame["city"] == city].set_index("date")
        plt.plot(city_data.index, city_data["temperature_mean"].rolling(7, min_periods=1).mean(),
                 label=city, linewidth=1.5)
    plt.title(f"Daily mean temperature: 7-day moving average, {period}")
    plt.xlabel("Date"); plt.ylabel("Temperature (°C)"); plt.legend(ncol=5)
    finish_plot("01_temperature_trends.png")
    plt.figure(figsize=(9, 5))
    sns.barplot(data=summary.reset_index(), x="city", y="precipitation_mm", color="#287f91", order=order)
    plt.title(f"Total precipitation by city, {period}")
    plt.xlabel("City"); plt.ylabel("Precipitation (mm)")
    finish_plot("02_precipitation.png")
    monthly = frame.pivot_table(index="city", columns="month", values="temperature_mean", aggfunc="mean")
    monthly = monthly.reindex(order)
    plt.figure(figsize=(11, 4.5))
    ax = sns.heatmap(monthly, annot=True, fmt=".1f", cmap="RdBu_r", center=0,
                     cbar_kws={"label": "Temperature (°C)"})
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0)
    plt.title(f"Mean temperature by city and month, {period}")
    plt.xlabel("Month"); plt.ylabel("City")
    finish_plot("03_monthly_heatmap.png")
    plt.figure(figsize=(9, 5))
    summary[["frost_days", "hot_days", "rainy_days"]].reindex(order).plot.bar(
        ax=plt.gca(), color=["#3e7cb1", "#d97735", "#4e9a79"], rot=0)
    plt.title(f"Weather exposure days, {period}")
    plt.xlabel("City"); plt.ylabel("Number of days")
    plt.legend(["Min < 0°C", "Max ≥ 30°C", "Precipitation ≥ 1 mm"])
    finish_plot("04_weather_exposure.png")
    plt.figure(figsize=(9, 5))
    sns.boxplot(data=frame, x="city", y="temperature_range", order=order, color="#8ab7c0")
    plt.title(f"Daily temperature range by city, {period}")
    plt.xlabel("City"); plt.ylabel("Daily max − min (°C)")
    finish_plot("05_temperature_range.png")
    save_json(METRICS / "eda.json", {"rows": len(frame), "columns": len(frame.columns),
        "dtypes": {key: str(value) for key, value in frame.dtypes.items()},
        "missing": int(frame.isna().sum().sum()), "figures": 5})
    warmest = summary["mean_temperature"].idxmax()
    wettest = summary["precipitation_mm"].idxmax()
    coldest = summary["mean_temperature"].idxmin()
    frostiest = summary["frost_days"].idxmax()
    ranges = frame.groupby("city")["temperature_range"].median()
    warm_city, warm_month = monthly.stack().idxmax()
    cold_city, cold_month = monthly.stack().idxmin()
    findings = f"""# Findings from the executed dataset

The SQLite database contains {len(frame)} daily records for {len(summary)} cities.
These are ERA5 reanalysis estimates, not raw measurements from city weather stations.

1. Temperature trends: {warmest} has the highest annual mean daily temperature
   ({summary.loc[warmest, 'mean_temperature']:.2f} °C); {coldest} has the lowest
   ({summary.loc[coldest, 'mean_temperature']:.2f} °C). The plot uses a trailing 7-day average.
2. Precipitation: {wettest} has the largest annual total
   ({summary.loc[wettest, 'precipitation_mm']:.1f} mm). Values include liquid-water-equivalent snowfall.
3. Monthly heatmap: the warmest city-month is {warm_city}, month {int(warm_month)}
   ({monthly.stack().max():.2f} °C), and the coldest is {cold_city}, month {int(cold_month)}
   ({monthly.stack().min():.2f} °C). Monthly aggregation makes seasonal differences visible.
4. Exposure days: {frostiest} has the most days with minimum temperature below 0 °C
   ({int(summary.loc[frostiest, 'frost_days'])}). Thresholds are descriptive, not official hazard warnings.
5. Temperature range: {ranges.idxmax()} has the largest median daily max-minus-min range
   ({ranges.max():.2f} °C). A boxplot shows variation and outliers without deleting valid extremes.

The within-month anomaly is relative to the same city and month in {period}. It is not
a climate anomaly relative to a multi-decade baseline. One year and five grid cells
cannot establish long-term climate change or a causal relationship.
"""
    (METRICS / "findings.md").write_text(findings, encoding="utf-8")
    print(f"EDA: {len(frame)} database rows, 5 figures", flush=True)
    return frame


# CLI
if __name__ == "__main__":
    run_analysis()
