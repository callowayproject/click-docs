"""Generate Markdown documentation for a Click command."""

from __future__ import annotations

import inspect
from typing import Iterator

import click


def generate_docs(
    command: click.Command,
    program_name: str | None = None,
    header_depth: int = 1,
    style: str = "plain",
) -> str:
    """
    Generate Markdown documentation for a Click command.

    Args:
        command: The Click command to document.
        program_name: Display name used in the heading and usage line.
            Defaults to the command's own ``name`` attribute.
        header_depth: Markdown header level for the command title (1–6).
        style: Options rendering style; ``"plain"`` (default) or ``"table"``.

    Returns:
        A Markdown string ending with a single newline.
    """
    if program_name is None:
        program_name = command.name or ""
    lines = list(_make_command_docs(command, program_name, header_depth, style))
    return "\n".join(lines) + "\n"


def _make_command_docs(
    command: click.Command,
    prog_name: str,
    header_depth: int = 1,
    style: str = "plain",
) -> Iterator[str]:
    """Yield Markdown lines for a single command (no recursion)."""
    ctx = command.make_context(prog_name, [], resilient_parsing=True)

    yield from _make_title(ctx, header_depth)
    yield from _make_description(ctx)
    yield from _make_usage(ctx)
    yield from _make_options(ctx, style)


def _make_title(ctx: click.Context, header_depth: int = 1) -> Iterator[str]:
    """Yield the command title as a Markdown heading at the given depth."""
    yield f"{'#' * header_depth} {ctx.info_name}"
    yield ""


def _make_description(ctx: click.Context) -> Iterator[str]:
    """Yield help text lines, truncating at ``\\f``."""
    help_text = ctx.command.help or ctx.command.short_help
    if not help_text:
        return
    help_text = inspect.cleandoc(help_text)
    help_text = help_text.partition("\f")[0]
    yield from help_text.splitlines()
    yield ""


def _make_usage(ctx: click.Context) -> Iterator[str]:
    """Yield a fenced-code usage block."""
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


def _make_options(ctx: click.Context, style: str = "plain") -> Iterator[str]:
    """Dispatch to the appropriate options renderer."""
    if style == "table":
        yield from _make_options_table(ctx)
    else:
        yield from _make_options_plain(ctx)


def _make_options_plain(ctx: click.Context) -> Iterator[str]:
    """Yield options as a fenced preformatted block from Click's own formatter.

    Help text is truncated at ``\\f`` before being passed to the formatter.
    """
    records = []
    for param in ctx.command.get_params(ctx):
        record = param.get_help_record(ctx)
        if record is None:
            continue
        name, help_text = record
        help_text = help_text.partition("\f")[0]
        records.append((name, help_text))

    if not records:
        return

    formatter = ctx.make_formatter()
    with formatter.section("Options"):
        formatter.write_dl(records)

    option_lines = formatter.getvalue().splitlines()[1:]  # strip "Options:" header
    if not option_lines:
        return

    yield "**Options:**"
    yield ""
    yield "```text"
    yield from option_lines
    yield "```"


def _make_options_table(ctx: click.Context) -> Iterator[str]:
    """Yield options as a Markdown table with Name, Type, and Description columns."""
    options = [p for p in ctx.command.params if isinstance(p, click.Option) and not _is_help_option(p)]
    if not options:
        return

    yield "**Options:**"
    yield ""
    yield "| Name | Type | Description |"
    yield "| --- | --- | --- |"
    for opt in options:
        name = " / ".join(opt.opts)
        type_str = _format_param_type(opt.type)
        help_text = (opt.help or "").partition("\f")[0].strip()
        yield f"| {name} | {type_str} | {help_text} |"
    yield ""


def _is_help_option(opt: click.Option) -> bool:
    """Return True if *opt* is the auto-generated ``--help`` flag."""
    return "--help" in opt.opts and opt.is_eager


def _format_param_type(param_type: click.ParamType) -> str:
    """Return a human-readable string for *param_type*, including constraints."""
    if isinstance(param_type, click.Choice):
        return f"one of: {', '.join(param_type.choices)}"
    if isinstance(param_type, (click.IntRange, click.FloatRange)):
        return _format_range(param_type)
    if isinstance(param_type, click.DateTime):
        return ", ".join(param_type.formats)
    if isinstance(param_type, click.File):
        return f"file ({param_type.mode})"
    return param_type.name.upper()


def _format_range(param_type: click.IntRange | click.FloatRange) -> str:
    """Render an IntRange or FloatRange as a bounds expression like ``0<=x<=10``."""
    min_op = "<" if getattr(param_type, "min_open", False) else "<="
    max_op = "<" if getattr(param_type, "max_open", False) else "<="
    parts = []
    if param_type.min is not None:
        parts.append(f"{param_type.min}{min_op}")
    parts.append("x")
    if param_type.max is not None:
        parts.append(f"{max_op}{param_type.max}")
    return "".join(parts)
