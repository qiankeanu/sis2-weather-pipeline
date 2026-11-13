-- Размер финальной таблицы
SELECT COUNT(*) AS stored_records FROM weather_daily;
-- Этот запрос не должен возвращать строки
SELECT city, date, COUNT(*) FROM weather_daily GROUP BY city, date HAVING COUNT(*) > 1;
-- Проверка охвата периода для каждого города
SELECT city, COUNT(*) AS days, MIN(date) AS first_day, MAX(date) AS last_day
FROM weather_daily GROUP BY city;
-- Аналитический запрос: холодные и жаркие дни
SELECT city, SUM(is_frost) AS frost_days, SUM(is_hot) AS hot_days,
       AVG(temperature_mean) AS mean_temperature, SUM(precipitation_mm) AS total_precipitation_mm
FROM weather_daily GROUP BY city ORDER BY mean_temperature DESC;
