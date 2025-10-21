# Repository Guidelines

## Project Structure & Module Organization
- Source (this folder `src/`): `main.py`, `book.py`, `author.py`.
- Tests: `test_book.py`, `test_main_stats.py` (pytest).
- Tooling: `Makefile`, `pyproject.toml`, `requirements.txt`, `uv.lock`, `.python-version`.
- Utilities: `cover-mosaic/` (cover mosaic Cloud Function), `bookmarklet/isbn.js` (ISBN helper).
- Data & outputs: run from `src/`. Reads `../data.json`; writes `../index.md`, `../books/`, `../authors/`, `../mosaic/index.html`.

## Build, Test, and Development Commands
- `uv venv bookcellent --python 3.13` then `make env`: create and activate venv.
- `make install`: install deps via `uv pip install -r requirements.txt`.
- `make build`: run `main.py` to (re)generate site content.
- `make test`: run pytest across the repo.
- `make clean`: remove caches and build artifacts.
- `make commit`: generate a conventional commit message via `ollama` and commit staged changes.
- `make deploy`: build, commit, push to `master`, and watch CI (requires `ollama`, `gh`, `jq`).

## Coding Style & Naming Conventions
- Python 3.13, PEP 8, 4‑space indentation. Modules/files are lower_snake_case; functions/methods `snake_case`.
- Keep relative paths stable; do not change the `../` output locations unless coordinating a site layout change.
- Prefer small, single‑purpose functions; add docstrings and type hints when practical.

## Testing Guidelines
- Framework: `pytest` (optional extra in `pyproject.toml`). Run with `make test`.
- Test files: `test_*.py`; name tests `test_<unit_under_test>_<behavior>()`.
- Cover decade/year grouping, per‑year progress, and thumbnail fallbacks; mock network calls in tests.

## Commit & Pull Request Guidelines
- Commits use Conventional Commits: `type: subject` in present tense.
  - Example: `feat: generate year and decade pages`.
- PRs include a clear description, linked issues, and test updates. Add screenshots or diffs of generated pages when relevant. Ensure CI passes.

## Security & Configuration Tips
- Do not commit secrets. External CLIs used: `uv`, `ollama`, `gh`, `jq`.
- Network calls fetch covers in `book.py` and `cover-mosaic/main.py`; prefer mocking in tests.
- Agents: keep changes minimal/surgical, preserve file layout, and update tests alongside code.

