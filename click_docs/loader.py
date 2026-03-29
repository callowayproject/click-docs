"""Load a Click command object from a file system path."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

import click


class LoadError(Exception):
    """Raised when a Click command cannot be loaded."""


def load_command(module_path: str, command_name: str = "cli") -> click.BaseCommand:
    """
    Load a Click command from a Python file.

    Args:
        module_path: File system path to the Python module (absolute or relative to cwd).
        command_name: Dotted attribute path on the module, e.g. ``cli`` or ``commands.root``.

    Returns:
        The resolved Click command object.

    Raises:
        LoadError: If the file does not exist, the attribute is missing, or the
            resolved object is not a Click command.
    """
    path = Path(module_path)
    if not path.exists():
        raise LoadError(f"Module path {str(module_path)!r} does not exist.")

    module = _load_module_from_path(path)
    obj = _resolve_dotted_attr(module, command_name, module_path)

    if not isinstance(obj, click.Command):
        raise LoadError(
            f"Attribute {command_name!r} in {str(module_path)!r} is not a Click command (got {type(obj).__name__!r})."
        )

    return obj


def _load_module_from_path(path: Path) -> Any:
    """Import a module from a file path and return the module object."""
    module_name = "_click_docs_loaded_module"
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:  # pragma: no cover
        raise LoadError(f"Cannot load module from {str(path)!r}.")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)  # type: ignore[union-attr]
    except Exception as exc:
        raise LoadError(f"Error importing {str(path)!r}: {exc}") from exc
    return module


def _resolve_dotted_attr(obj: Any, dotted_path: str, source: str) -> Any:
    """Walk a dotted attribute path on *obj*, raising LoadError if any segment is missing."""
    parts = dotted_path.split(".")
    current = obj
    for part in parts:
        if not hasattr(current, part):
            raise LoadError(f"{source!r} has no attribute {part!r} (in path {dotted_path!r}).")
        current = getattr(current, part)
    return current
