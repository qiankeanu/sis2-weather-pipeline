# Dauirkhankyzy Balnur — 23B031274

Часть: API collection and original data.
Репозиторий: https://github.com/qiankeanu/sis2-weather-pipeline
Данные: 01.01.2025–31.12.2025, 1 825 дневных записей пяти городов.

Для изучения: реальные исходные JSON/CSV уже приложены; для нового сбора нужен интернет.

## Команды для терминала VS Code

Сначала Kian должен дать вам доступ Collaborator; примите приглашение.
Распакуйте этот пакет вне репозитория. Команда import_part принимает путь к папке `01_Balnur`,
в которой лежат `package_manifest.json` и `upload_to_repo/`.

```bash
git clone https://github.com/qiankeanu/sis2-weather-pipeline.git
cd sis2-weather-pipeline
git switch -c codex/balnur-api
python scripts/import_part.py "/ПУТЬ/К/01_Balnur"
git status --short
git add -- data/raw_data.csv data/raw_data.json data/raw_responses/almaty.json data/raw_responses/astana.json data/raw_responses/atyrau.json data/raw_responses/karaganda.json data/raw_responses/shymkent.json docs/data_dictionary.md results/collection.json src/api_client.py
git diff --cached --stat
git commit -m 'Add API collection and preserved weather data'
git push -u origin codex/balnur-api
```

Замените только путь `/ПУТЬ/К/01_Balnur` на свой. Если команда `python` не найдена,
используйте `python3` (macOS/Linux) или `py` (Windows).
Перед коммитом изучите, запустите и проверьте свои файлы. Все входные данные для отдельного
ноутбука находятся в `study_only/`: запустите его отдельно от клона, по приложенному README.

На GitHub нажмите Compare & pull request. Base: `main`, compare: `codex/balnur-api`.
Создайте pull request, укажите свои изменения и что проверили; Kian объединит его.
Не загружайте сам ZIP, `study_only/`, `.venv/`, `.runtime/` или папку `01_Balnur` целиком.

## Только ваши файлы для коммита

- `data/raw_data.csv`
- `data/raw_data.json`
- `data/raw_responses/almaty.json`
- `data/raw_responses/astana.json`
- `data/raw_responses/atyrau.json`
- `data/raw_responses/karaganda.json`
- `data/raw_responses/shymkent.json`
- `docs/data_dictionary.md`
- `results/collection.json`
- `src/api_client.py`
