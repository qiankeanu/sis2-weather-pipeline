# Команда SIS 2

Учебная группа: **Group 7**.

Тема: Weather Data Streaming and Validation Pipeline for Five Cities in Kazakhstan.
Период: 01.01.2025–31.12.2025. Источник: Open-Meteo Historical Weather API / ERA5.
В этом файле записано распределение ответственности. Оно не является утверждением,
что каждый участник уже самостоятельно выполнил и защитил свою часть.

| Участник | Student ID | Ответственность | Файлы для своей ветки |
|---|---|---|---|
| Dauirkhankyzy Balnur | 23B031274 | API-запросы, ошибки HTTP, сохранение исходных ответов, первичный обзор данных | `src/api_client.py`, `src/config.py`, `src/common.py`, `notebooks/01_Balnur_API.ipynb`, `docs/data_dictionary.md`, `data/raw*`, `results/collection.json` |
| Abibulla Kundyz | 23B030352 | Настоящий Kafka, topic, JSON Producer/Consumer, счётчики сообщений и завершение чтения | `src/producer.py`, `src/consumer.py`, `docker-compose.yml`, `scripts/start_kafka_local.py`, `notebooks/02_Kundyz_Kafka.ipynb`, `data/consumed*`, `results/producer.json`, `results/consumer.json` |
| Kalybay Nurdaulet | 23B031515 | Pandera, изолированные ошибочные примеры, pandas/NumPy, GroupBy, pivot | `src/validator.py`, `src/cleaner.py`, `notebooks/03_Nurdaulet_Validation_Cleaning.ipynb`, `data/valid_data.csv`, `data/invalid_data.csv`, `data/cleaned_data.csv`, `data/hot_dry_days.csv`, `data/test_only/`, результаты проверки и очистки |
| Dauletkhan Kian | 23B031082 | SQLite, SQL, проверка повторной загрузки, EDA, выводы, интеграция всей цепочки | `src/loader.py`, `src/analysis.py`, `src/verification.py`, `main.py`, `sql/`, `tests/`, `notebooks/04_Kian_SQLite_EDA_Evaluation.ipynb`, `figures/`, документация запуска |

## Как передавать работу

В папке `handoff/` находятся четыре ZIP-пакета. В каждом есть личный ноутбук,
соответствующие `.py`, общие настройки, README и необходимые входные данные.
Общие настройки нужно объединить первыми, затем Kafka, затем валидацию/очистку,
затем SQLite/EDA и интеграцию. Участники не должны коммитить свои `.venv` или `.runtime`.

После создания общего удалённого репозитория каждый клонирует его и создаёт ветку:

```bash
git switch -c codex/balnur-api
# Остальные: codex/kundyz-kafka, codex/nurdaulet-validation, codex/kian-database-eda
git add <свои файлы из таблицы>
git commit -m "Add API collection and preserved weather data"
git push -u origin codex/balnur-api
```

Перед коммитом прочитайте код, выполните свою часть, проверьте результаты и внесите
свои понятные улучшения. Укажите фактический вклад в отчёте после работы команды.
Все четверо должны понимать весь пайплайн, включая код других участников.

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
