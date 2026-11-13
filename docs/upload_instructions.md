# Загрузка частей в общий репозиторий

Репозиторий: https://github.com/qiankeanu/sis2-weather-pipeline
Группа: Group 7. Данные: 01.01.2025–31.12.2025, пять городов, 1 825 записей.

Первым Kian загружает общую основу и свою часть. Остальные добавляют только собственные
файлы через отдельные ветки и pull request. После объединения всех частей Kian проверяет
полный проект и формирует итоговый PDF-отчёт локально для сдачи преподавателю. Текущая база и результаты получены настоящим
запуском; частичный репозиторий ещё не является полной сдачей.

## Кому какой пакет отправить

| Участник | ZIP | Вход для изучения | Что загружает |
|---|---|---|---|
| Balnur | SEND_01_Balnur.zip | сохранённые API JSON/CSV | API-клиент, словарь полей, raw_data, raw_responses, collection.json |
| Kundyz | SEND_02_Kundyz.zip | raw_data и collection.json от Balnur | Kafka-код и настройка, consumed_data, метрики Producer/Consumer |
| Nurdaulet | SEND_03_Nurdaulet.zip | consumed_data и метрики от Kundyz | Pandera, очистка, valid/invalid/cleaned CSV, отдельные плохие тесты, группировки |
| Kian | SEND_04_Kian.zip | cleaned_data и метрики остальных | SQLite, SQL, EDA, evaluation, интеграция, база, графики и тесты |

В каждом ZIP есть:

- `upload_to_repo/` — только личные файлы для репозитория, с сохранением путей `src/`, `data/`, `results/`.
- `study_only/` — личный ноутбук и входные файлы для отдельного запуска. Это не загружается в репозиторий.
- `HOW_TO_UPLOAD.md` — персональные команды, включая точный `git add`.
- `package_manifest.json` — список личных файлов и контрольных сумм.

Не загружайте ZIP целиком и не создавайте в репозитории папку с именем участника.
Скрипт `scripts/import_part.py` безопасно добавляет личные файлы внутрь общих папок.
Не копируйте целую папку `src` с заменой: это может затереть чужие файлы.

## Доступ и порядок работы

Kian добавляет GitHub-аккаунты участников в Settings → Collaborators → Add people;
каждый принимает приглашение. Публичность позволяет читать репозиторий, но сама по себе
не даёт право push. Без write-доступа используйте fork и pull request из своего fork.

Для каждого участника:

1. Распаковать свой `SEND_...zip` в отдельную папку вне клона.
2. Клонировать общий репозиторий и создать свою ветку (команды в личном файле).
3. Выполнить `python scripts/import_part.py "ПУТЬ_К_РАСПАКОВАННОЙ_ЛИЧНОЙ_ПАПКЕ"`.
4. Прочитать и проверить собственный код, выполнить доступную часть, изучить результаты.
5. Выполнить персональные `git add`, `git commit`, `git push`.
6. На GitHub выбрать Compare & pull request, base: main, compare: личная ветка,
   затем Create pull request. Kian проверяет и объединяет изменения.

Каждый использует свой GitHub-аккаунт и собственные git user.name/user.email.
Не подменяйте автора коммита и не выдавайте согласованное распределение за уже выполненную
личную работу: перед коммитом разберите, запустите и подтвердите свою часть.

Рекомендуемый порядок объединения: Balnur → Kundyz → Nurdaulet → итоговая проверка Kian.
Все три ветки можно создать от текущей main: личные файлы не пересекаются.

## Финальная проверка после объединения

```bash
python -m pip install -r requirements-dev.txt
python scripts/start_kafka_local.py
# Во втором терминале с тем же Python-окружением:
python main.py --use-snapshot
python -m pytest -q
python -m pip install -r requirements-report.txt
python scripts/build_report.py --group 7
```

После этого Kian обновляет статус README и проверяет соответствие локального отчёта итоговому коду.
Полный PDF с учебными идентификаторами не загружается в публичный репозиторий.

Официальные инструкции:
- https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository
- https://docs.github.com/en/pull-requests/how-tos/create-pull-requests/creating-a-pull-request
