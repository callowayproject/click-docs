# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`click-docs` is a Python library that generates Markdown documentation from Click CLI applications. It introspects Click command objects and produces formatted Markdown with usage info, options, and nested command hierarchies.

## Commands

This project uses `uv` for package management.

Add `--agent-digest=terminal` to `uv run pytest` commands to optimize test output.

```bash
# Install all dependency groups
uv sync --all-groups

# Run all tests
uv run pytest --agent-digest=terminal

# Run a single test file
uv run pytest --agent-digest=terminal tests/test_core/test_indented_logger.py

# Run a single test by name
uv run pytest --agent-digest=terminal tests/test_core/test_indented_logger.py::test_function_name

# Lint (check only)
ruff check .

# Format check
ruff format --check .

# Auto-fix lint and format
ruff check --fix . && ruff format .

# Type checking
mypy click_docs

# Install pre-commit hooks (one-time setup)
pre-commit install

# Run pre-commit on all files
pre-commit run --all-files
```

## Architecture

The project has three core modules:

**`click_docs/loader.py`** — Dynamic module loading. Takes a filesystem path to a Python file, imports it as a module, and resolves a dotted attribute path to find the Click command object.

**`click_docs/generator.py`** — Core documentation generation. `generate_docs()` is the main entry point. It recursively traverses Click command groups, rendering each command's usage, description, and options to Markdown. Supports two rendering styles (`plain` / `table`), configurable header depth, command exclusions, hidden command filtering, and ASCII art (`\b` block) removal.

**`click_docs/cli.py`** — CLI interface. Wires together loader and generator, exposing all generator options as Click flags.

## Data Flow

```
click-docs <module_path> [options]
  → cli.py parses options
  → loader.py imports the module and resolves the Click command object
  → generator.py recursively generates Markdown
  → stdout or --output file
```

## Testing

Tests live in `tests/`. The fixture Click application used across tests is `tests/app/cli.py` — it contains nested groups, hidden commands/options, special parameter types, and ASCII art blocks. When adding new generator features, add corresponding fixtures there.

CI runs on Python 3.12 and 3.13 via GitHub Actions (`.github/workflows/test.yaml`), triggered on changes to `click_docs/*` or `tests/*`.

## Code Style

- Docstrings: Google style (enforced by `pydoclint`, coverage ≥90% via `interrogate`)
- Type annotations: Required on all functions (enforced by ruff `ANN` rules)
- Ruff preview mode is enabled with strict rules — run `ruff check` before committing
