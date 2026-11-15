# Data dictionary

One raw record = one city × one local calendar date. Date boundary: Asia/Almaty (UTC+5).
API model: ERA5 reanalysis, requested explicitly for a consistent model across cities and dates.
Grid-cell coordinates may differ from the requested city coordinates; both are documented.
API fields are flattened without cleaning; a record ID and city label are added as provenance.

| Column | Type | Unit / meaning | Validation or origin |
|---|---|---|---|
| record_id | string | lowercase city + `_` + ISO date | matches city/date; database primary key |
| city | categorical string | one of five cities | configured allowed list |
| date | ISO date | local day | valid calendar date in collection period |
| temperature_min | number | °C, daily minimum at 2 m | required; −90 to 65 |
| temperature_max | number | °C, daily maximum at 2 m | required; −90 to 65; min ≤ max |
| temperature_mean | number / null | °C, daily mean at 2 m | −90 to 65; between min/max; optional null |
| precipitation_mm | number | mm, daily precipitation including snowfall water equivalent | required; 0 to 2,000 |
| wind_max_kmh | number | km/h, daily max wind speed at 10 m | required; 0 to 500 |
| weather_code | category stored as integer | daily WMO weather code | allowed official codes |

Broad physical boundaries detect impossible values; they do not censor genuine local extremes.
Numbers must be finite numeric values, not arbitrary text or booleans. Dates are strings during
validation and are explicitly converted to pandas datetime only during cleaning.
Invalid required values are quarantined, not silently corrected. A missing optional mean is
estimated from `(min + max)/2`, explicitly flagged, and not described as an observed daily mean.

| Added column | Type | Meaning |
|---|---|---|
| mean_was_imputed | 0/1 | daily mean was estimated from min/max |
| temperature_range | number, °C | NumPy max − min |
| month | integer 1–12 | month of local date |
| season | category | meteorological Winter/Spring/Summer/Autumn |
| is_rainy | 0/1 | precipitation ≥ 1 mm; includes snow water equivalent |
| is_frost | 0/1 | daily minimum < 0°C |
| is_hot | 0/1 | daily maximum ≥ 30°C |
| temperature_anomaly | number, °C | daily mean minus city/month mean within this dataset |

The name `is_rainy` is a shorthand for a wet day, not proof of liquid rain.
Anomalies use a one-year city/month baseline, not the standard multi-decade climate baseline.

Source and WMO code definitions: https://open-meteo.com/en/docs/historical-weather-api
