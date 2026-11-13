# Findings from the executed dataset

The SQLite database contains 1825 daily records for 5 cities.
These are ERA5 reanalysis estimates, not raw measurements from city weather stations.

1. Temperature trends: Shymkent has the highest annual mean daily temperature
   (15.09 °C); Astana has the lowest
   (5.46 °C). The plot uses a trailing 7-day average.
2. Precipitation: Almaty has the largest annual total
   (647.2 mm). Values include liquid-water-equivalent snowfall.
3. Monthly heatmap: the warmest city-month is Shymkent, month 7
   (29.62 °C), and the coldest is Karaganda, month 2
   (-10.72 °C). Monthly aggregation makes seasonal differences visible.
4. Exposure days: Astana has the most days with minimum temperature below 0 °C
   (180). Thresholds are descriptive, not official hazard warnings.
5. Temperature range: Shymkent has the largest median daily max-minus-min range
   (13.70 °C). A boxplot shows variation and outliers without deleting valid extremes.

The within-month anomaly is relative to the same city and month in 2025. It is not
a climate anomaly relative to a multi-decade baseline. One year and five grid cells
cannot establish long-term climate change or a causal relationship.
