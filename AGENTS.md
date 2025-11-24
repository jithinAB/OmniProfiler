# Repository Guidelines

## Project Structure & Module Organization
Core Python lives in `code/`: `code/profiler/` holds the orchestrator plus hardware/static/dynamic analyzers (see `docs/architecture.md`), `code/api/` is the FastAPI entry point, and `code/cli.py` supplies Typer commands; supporting materials sit in `scripts/`, `examples/`, and `docs/`. Tests mirror module boundaries in `tests/`, and the React/Vite dashboard resides in `ui/` (`src/`, `public/`, `dist/`) to communicate with the API.

## Build, Test, and Development Commands
- `python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt` — backend environment bootstrap.
- `python -m code.cli serve --host 0.0.0.0 --port 8000` — run the FastAPI service with reload.
- `python -m code.cli profile examples/sample_script.py` — smoke-test the profiling pipeline.
- `python scripts/automated_profiling.py --benchmarks --scales small,medium` — execute workloads into `results/`.
- `pytest` (or `pytest tests/workloads/test_generators.py -k medium`) — run tests with coverage from `pytest.ini`.
- `cd ui && npm install && npm run dev` for the dashboard; `npm run build` produces `ui/dist/`.

## Coding Style & Naming Conventions
Follow PEP 8 with 4-space indents, type hints on public APIs, and dataclasses for structured metrics (see `code/profiler/metrics/`). Modules stay snake_case and descriptive (`hardware.py`, `repo_fetcher.py`); new workloads belong in `code/profiler/workloads/` with scale-aware names (e.g., `generate_orders_large`). Frontend code prefers functional React components, PascalCase filenames in `ui/src/components/`, and linting via `npm run lint`.

## Testing Guidelines
`pytest.ini` limits collection to `tests/` and enforces `--cov=code/profiler --cov-report=term-missing`, so maintain ≥75 % coverage and include negative-path assertions when editing orchestrator logic. Tests should mirror module paths (`tests/profiler/test_orchestrator.py`) and can lean on workload generators for repeatable fixtures. Regression scripts should assert numerical metrics plus schema keys in `hardware`, `static_analysis`, and `dynamic_analysis`. UI tweaks need verification in `npm run dev`; add Vitest/Jest checks when behavior warrants extra guardrails.

## Commit & Pull Request Guidelines
Use imperative Conventional Commit subjects with scoped prefixes—`fix(orchestrator): refresh hardware snapshot`, `feat(ui): add workload selector`. PRs should summarize behavior changes, quote verification commands (`pytest`, profiling scripts, UI screenshots), link issues or docs, and note performance/security impacts. Keep each PR focused on a single surface (profiler, API, UI, or automation) to simplify reviews.

## Security & Configuration Tips
Profiling executes arbitrary code, so keep `RepoFetcher` artifacts isolated and restrict builtins whenever touching exec paths (see `NEW_ISSUES_FOUND.md`). Do not raise the file/code size limits in `code/api/main.py` without updating docs and safeguards. Configure API URLs through `.env` (see `ui/.env.example`) instead of hard-coding, and call cleanup utilities after profiling runs to avoid dangling clones or logs.
