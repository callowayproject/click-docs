"""Generate Markdown documentation for a Click command."""

from __future__ import annotations

import inspect
from typing import Iterator

import click


def generate_docs(command: click.Command, program_name: str | None = None) -> str:
    """
    Generate Markdown documentation for a Click command.

    Args:
        command: The Click command to document.
        program_name: Display name used in the heading and usage line.
            Defaults to the command's own ``name`` attribute.

    Returns:
        A Markdown string ending with a single newline.
    """
    if program_name is None:
        program_name = command.name or ""
    lines = list(_make_command_docs(command, program_name))
    return "\n".join(lines) + "\n"


def _make_command_docs(command: click.Command, prog_name: str) -> Iterator[str]:
    """Yield Markdown lines for a single command (no recursion)."""
    ctx = command.make_context(prog_name, [], resilient_parsing=True)

    yield from _make_title(ctx)
    yield from _make_description(ctx)
    yield from _make_usage(ctx)
    yield from _make_options(ctx)


def _make_title(ctx: click.Context) -> Iterator[str]:
    """
    Generates and yields lines for a title formatted based on the provided Click context.

    Args:
        ctx: The Click context object containing command metadata, including help text.

    Yields:
        str: Lines representing the formatted title.
    """
    yield f"# {ctx.info_name}"
    yield ""


def _make_description(ctx: click.Context) -> Iterator[str]:
    """
    Generates an iterator of help text lines for a given Click context.

    This function retrieves the help or short help text from the provided
    Click context and processes it by cleaning and splitting into individual
    lines. If no help text is available, the function returns nothing.

    Args:
        ctx: The Click context object containing command metadata, including help text.

    Yields:
        str: An iterator yielding individual lines of the processed help text, followed by an empty line.
    """
    help_text = ctx.command.help or ctx.command.short_help
    if not help_text:
        return
    help_text = inspect.cleandoc(help_text)
    help_text = help_text.partition("\f")[0]
    yield from help_text.splitlines()
    yield ""


def _make_usage(ctx: click.Context) -> Iterator[str]:
    """
    Generates a formatted usage guide for a given Click command context.

    This function produces an iterator that yields strings representing the usage
    guide for the provided command. The guide includes usage information formatted
    with the appropriate prefix and styling.

    Args:
        ctx: The Click context object containing metadata about the current command and its configuration.

    Yields:
        str: A formatted string representing a portion of the usage guide.
            The iterator provides individual sections of the guide sequentially.
    """
    formatter = ctx.make_formatter()
    pieces = ctx.command.collect_usage_pieces(ctx)
    formatter.write_usage(ctx.command_path, " ".join(pieces), prefix="")
    usage = formatter.getvalue().strip()

    yield "**Usage:**"
    yield ""
    yield "```text"
    yield usage
    yield "```"
    yield ""


def _make_options(ctx: click.Context) -> Iterator[str]:
    """
    Generates an iterator of formatted option strings for a Click command context.

    This function takes a Click command context, formats its options using the
    command's formatting utilities, and yields the formatted option strings as an
    iterator. It omits any header lines and properly formats the output with a
    markdown-like structure.

    Args:
        ctx: The Click command context from which to extract and format options.

    Yields:
        str: A line of formatted option strings, including markdown-like markup for the structured display.

    """
    formatter = ctx.make_formatter()
    click.Command.format_options(ctx.command, ctx, formatter)
    option_lines = formatter.getvalue().splitlines()[1:]  # strip "Options:" header

    if not option_lines:
        return

    yield "**Options:**"
    yield ""
    yield "```text"
    yield from option_lines
    yield "```"
