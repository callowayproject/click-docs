"""Command-line entry point for click-docs."""

from __future__ import annotations

import sys
from pathlib import Path

import click

from .generator import generate_docs
from .loader import LoadError, load_command


@click.command()
@click.argument("module_path")
@click.option(
    "--command-name",
    default="cli",
    show_default=True,
    help="Dotted attribute path to the Click command object.",
)
@click.option(
    "--output",
    default=None,
    metavar="FILE",
    help="Write output to FILE instead of stdout.",
)
def cli(module_path: str, command_name: str, output: str | None) -> None:
    """
    Generate Markdown documentation for a Click application.

    MODULE_PATH is a file system path to the Python module containing the Click command.
    """
    try:
        command = load_command(module_path, command_name)
    except LoadError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)

    markdown = generate_docs(command)

    if output is None:
        click.echo(markdown, nl=False)
        return

    out_path = Path(output)
    if not out_path.parent.exists():
        click.echo(f"Error: Output directory {str(out_path.parent)!r} does not exist.", err=True)
        sys.exit(1)

    out_path.write_text(markdown, encoding="utf-8")
