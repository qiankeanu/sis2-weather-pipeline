# Команда SIS 2

Учебная группа: **Group 7**.

Тема: Weather Data Streaming and Validation Pipeline for Five Cities in Kazakhstan.
Период: 01.01.2025–31.12.2025. Источник: Open-Meteo Historical Weather API / ERA5.
В этом файле записано распределение ответственности. Оно не является утверждением,
что каждый участник уже самостоятельно выполнил и защитил свою часть.

| Участник | Ответственность | Файлы для своей ветки |
|---|---|---|
| Balnur | API-запросы, ошибки HTTP, сохранение исходных ответов, первичный обзор данных | `src/api_client.py`, `src/config.py`, `src/common.py`, `docs/data_dictionary.md`, `data/raw*`, `results/collection.json` |
| Kundyz | Настоящий Kafka, topic, JSON Producer/Consumer, счётчики сообщений и завершение чтения | `src/producer.py`, `src/consumer.py`, `docker-compose.yml`, `scripts/start_kafka_local.py`, `data/consumed*`, `results/producer.json`, `results/consumer.json` |
| Nurdaulet | Pandera, изолированные ошибочные примеры, pandas/NumPy, GroupBy, pivot | `src/validator.py`, `src/cleaner.py`, `data/valid_data.csv`, `data/invalid_data.csv`, `data/cleaned_data.csv`, `data/hot_dry_days.csv`, `data/test_only/`, результаты проверки и очистки |
| Kian | SQLite, SQL, проверка повторной загрузки, EDA, выводы, интеграция всей цепочки | `src/loader.py`, `src/analysis.py`, `src/verification.py`, `main.py`, `sql/`, `tests/`, `figures/`, документация запуска |

## Как передавать работу

Используйте новые `handoff/SEND_01_Balnur.zip`, `SEND_02_Kundyz.zip`,
`SEND_03_Nurdaulet.zip`, `SEND_04_Kian.zip`. В `upload_to_repo/` находятся только
личные файлы для коммита; в `study_only/` — ноутбук и чужие входные данные для запуска.
Точный список владельцев находится в `docs/upload_manifest.json`.
Пошаговые команды: `docs/upload_instructions.md` и личный `HOW_TO_UPLOAD.md`.

## Вопросы для защиты

- Balnur: чем API отличается от CSV, что такое HTTP timeout, зачем хранить полный JSON,
  чем координаты запроса отличаются от координат ячейки ERA5?
- Kundyz: broker/topic/partition, зачем JSON, почему считаем подтверждённые сообщения,
  зачем run_id, как Consumer заканчивает работу и что происходит при повторном запуске?
- Nurdaulet: зачем проверка до очистки, почему мороз не является ошибкой,
  что делать с пропусками, чем GroupBy отличается от pivot, зачем отдельные плохие тесты?
- Kian: primary key, UNIQUE, почему повторная вставка не меняет базу,
  как SQL подтверждает данные, что означают графики и почему год данных не доказывает изменение климата?

Ноутбуки созданы для изучения и передачи частей. В исходном PDF сдача `.ipynb`
не принимается; рабочий вариант для сдачи — модули `.py` и документация.

Публичная версия содержит только имена участников. Полные имена и student ID хранятся локально в игнорируемой `.private/`.
