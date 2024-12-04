# Chrome History Script

Linux版Chromeの閲覧履歴データを月を指定してTSVダンプするスクリプト。

- Python 3.12
- Poetry 1.8

```shell
poetry install

./copy_history.sh

poetry run python dump_history.py
```

## コードフォーマット

```shell
poetry run ruff check --fix
poetry run ruff format

poetry run mypy .
```
