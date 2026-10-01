# ITMO: Python (base)

## Project

Educational repo for the **ITMO: Python (base)** course. Covers Python syntax, data types, OOP, and standard library modules. Tasks are placed in subdirectories.

## Running code

```bash
source .venv/bin/activate
python3 <file>.py
```

Python 3.14. No external dependencies. No linter/formatter — follow PEP 8.

## Structure

- `.py` files go in the project root or task-specific subdirectories
- `.venv/`, `.idea/` — ignored (parent `.gitignore` covers them)
- No `pyproject.toml`, `requirements.txt`, or test framework configured

## Commits

Prefix format: `F-*: <desc>` for tasks and features.
Branches: `features/f-*`.
