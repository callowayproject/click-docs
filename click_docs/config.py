"""Configuration loading from pyproject.toml for click-docs."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def find_config(start: Path | None = None) -> dict[str, Any]:
    """
    Searches for a 'pyproject.toml' file starting from a given directory and traversing up the directory tree.

    If found, the configuration file is read and returned as a dictionary. If no configuration file is found, an
    empty dictionary is returned.

    Args:
        start: Starting directory path to begin the search for 'pyproject.toml'. If None, the current
            working directory is used.

    Returns:
        A dictionary containing the configuration data parsed from 'pyproject.toml'. Returns an empty
        dictionary if no configuration file is located.
    """
    if start is None:
        start = Path.cwd()

    current = Path(start).resolve()
    while True:
        candidate = current / "pyproject.toml"
        if candidate.is_file():
            return _read_config(candidate)
        parent = current.parent
        if parent == current:
            return {}
        current = parent


def _read_config(path: Path) -> dict[str, Any]:
    """
    Read the *[tool.click-docs]* section from a pyproject.toml file.

    Args:
        path: Path to the pyproject.toml file.

    Returns:
        Dict of *[tool.click-docs]* values, or empty dict if the section is absent.
    """
    try:
        import tomllib
    except ImportError:
        import tomli as tomllib  # type: ignore[no-redef]

    with path.open("rb") as f:
        data = tomllib.load(f)

    return data.get("tool", {}).get("click-docs", {})
