"""Command-line entry point for click-docs."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import click
from click.core import ParameterSource

from .config import find_config
from .generator import generate_docs
from .loader import LoadError, load_command

# Maps Python parameter names (underscores) to pyproject.toml keys (hyphens).
_PARAM_TO_CONFIG_KEY: dict[str, str] = {
    "command_name": "command-name",
    "program_name": "program-name",
    "header_depth": "header-depth",
    "style": "style",
    "output": "output",
    "depth": "depth",
    "show_hidden": "show-hidden",
    "list_subcommands": "list-subcommands",
    "remove_ascii_art": "remove-ascii-art",
    "full_command_path": "full-command-path",
}


def _apply_config(ctx: click.Context, config: dict[str, Any], kwargs: dict[str, Any]) -> dict[str, Any]:
    """Override defaulted CLI params with values from config.

    Args:
        ctx: The Click context for the current invocation.
        config: Dict of [tool.click-docs] values from pyproject.toml.
        kwargs: Current parameter values keyed by Python name (underscores).

    Returns:
        Updated kwargs dict with config values applied where CLI used its default.
    """
    result = dict(kwargs)
    for param, config_key in _PARAM_TO_CONFIG_KEY.items():
        if ctx.get_parameter_source(param) == ParameterSource.DEFAULT and config_key in config:
            result[param] = config[config_key]
    if ctx.get_parameter_source("exclude") == ParameterSource.DEFAULT and "exclude" in config:
        result["exclude"] = tuple(config["exclude"])
    return result


@click.command()
@click.pass_context
@click.argument("module_path")
@click.option(
    "--command-name",
    default="cli",
    show_default=True,
    help="Dotted attribute path to the Click command object.",
)
@click.option(
    "--program-name",
    default=None,
    help="Display name for the command in headings and usage lines.",
)
@click.option(
    "--header-depth",
    default=1,
    show_default=True,
    type=click.IntRange(1, 6),
    help="Markdown header level for the command title (1-6).",
)
@click.option(
    "--style",
    default="plain",
    show_default=True,
    type=click.Choice(["plain", "table"]),
    help="Options rendering style.",
)
@click.option(
    "--output",
    default=None,
    metavar="FILE",
    help="Write output to FILE instead of stdout.",
)
@click.option(
    "--depth",
    default=None,
    type=click.IntRange(min=0),
    metavar="N",
    help="Maximum subcommand recursion depth (0=root only; default=unlimited).",
)
@click.option(
    "--exclude",
    multiple=True,
    metavar="PATH",
    help="Dotted command path to exclude (e.g. root.admin.reset). Repeatable.",
)
@click.option(
    "--show-hidden",
    is_flag=True,
    default=False,
    help="Include commands and options marked hidden=True.",
)
@click.option(
    "--list-subcommands",
    is_flag=True,
    default=False,
    help="Prepend a bulleted TOC of subcommands at the root level.",
)
@click.option(
    "--remove-ascii-art",
    is_flag=True,
    default=False,
    help=r"Strip \b-prefixed blocks (ASCII art) from help text.",
)
@click.option(
    "--full-command-path",
    is_flag=True,
    default=False,
    help="Use the full command path in headers (e.g. 'cli admin' instead of 'admin').",
)
def cli(
    ctx: click.Context,
    module_path: str,
    command_name: str,
    program_name: str | None,
    header_depth: int,
    style: str,
    output: str | None,
    depth: int | None,
    exclude: tuple[str, ...],
    show_hidden: bool,
    list_subcommands: bool,
    remove_ascii_art: bool,
    full_command_path: bool,
) -> None:
    """
    Generate Markdown documentation for a Click application.

    MODULE_PATH is a file system path to the Python module containing the Click command.
    """
    resolved = _apply_config(
        ctx,
        find_config(),
        {
            "command_name": command_name,
            "program_name": program_name,
            "header_depth": header_depth,
            "style": style,
            "output": output,
            "depth": depth,
            "exclude": exclude,
            "show_hidden": show_hidden,
            "list_subcommands": list_subcommands,
            "remove_ascii_art": remove_ascii_art,
            "full_command_path": full_command_path,
        },
    )

    try:
        command = load_command(module_path, resolved["command_name"])
    except LoadError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)

    markdown = generate_docs(
        command,
        program_name=resolved["program_name"],
        header_depth=resolved["header_depth"],
        style=resolved["style"],
        depth=resolved["depth"],
        exclude=resolved["exclude"],
        show_hidden=resolved["show_hidden"],
        list_subcommands=resolved["list_subcommands"],
        remove_ascii_art=resolved["remove_ascii_art"],
        full_command_path=resolved["full_command_path"],
    )

    if resolved["output"] is None:
        click.echo(markdown, nl=False)
        return

    out_path = Path(resolved["output"])
    if not out_path.parent.exists():
        click.echo(f"Error: Output directory {str(out_path.parent)!r} does not exist.", err=True)
        sys.exit(1)

    out_path.write_text(markdown, encoding="utf-8")
