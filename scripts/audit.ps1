$ErrorActionPreference = "Stop"

$env:PYTHONUTF8 = "1"

& .\.venv\Scripts\python -m compileall config.py src tests
& .\.venv\Scripts\ruff check .
& .\.venv\Scripts\python -m mypy config.py src\infra\llm
& .\.venv\Scripts\bandit -q -r src
& .\.venv\Scripts\pip-audit -r requirements.txt --strict
