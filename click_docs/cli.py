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
    try:
        command = load_command(module_path, command_name)
    except LoadError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)

    markdown = generate_docs(
        command,
        program_name=program_name,
        header_depth=header_depth,
        style=style,
        depth=depth,
        exclude=exclude,
        show_hidden=show_hidden,
        list_subcommands=list_subcommands,
        remove_ascii_art=remove_ascii_art,
        full_command_path=full_command_path,
    )

    if output is None:
        click.echo(markdown, nl=False)
        return

    out_path = Path(output)
    if not out_path.parent.exists():
        click.echo(f"Error: Output directory {str(out_path.parent)!r} does not exist.", err=True)
        sys.exit(1)

    out_path.write_text(markdown, encoding="utf-8")
