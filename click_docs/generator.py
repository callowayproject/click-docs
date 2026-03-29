"""Generate Markdown documentation for a Click command."""

from __future__ import annotations

import inspect
import re
from contextlib import ExitStack, contextmanager
from typing import Iterator

import click


def generate_docs(
    command: click.BaseCommand,
    program_name: str | None = None,
    header_depth: int = 1,
    style: str = "plain",
    depth: int | None = None,
    exclude: tuple[str, ...] | list[str] = (),
    show_hidden: bool = False,
    list_subcommands: bool = False,
    remove_ascii_art: bool = False,
    full_command_path: bool = False,
) -> str:
    """
    Generate Markdown documentation for a Click command.

    Args:
        command: The Click command to document.
        program_name: The display name used in the heading and usage line.
            Defaults to the command's own ``name`` attribute.
        header_depth: Markdown header level for the command title (1-6).
        style: Options rendering style; ``"plain"`` (default) or ``"table"``.
        depth: Maximum recursion depth. ``0`` = root only, ``None`` = unlimited.
        exclude: Dotted command paths to skip (e.g. ``("root.admin.reset",)``).
            The root command name is the first segment.
        show_hidden: Include commands and options marked ``hidden=True``.
        list_subcommands: Prepend a bulleted TOC of direct subcommands at the root.
        remove_ascii_art: Strip ``\\b``-prefixed blocks (up to the next blank line).
        full_command_path: Use the full command path in headers (e.g. ``cli admin``).

    Returns:
        A Markdown string ending with a single newline.
    """
    if program_name is None:
        program_name = command.name or ""
    exclude_set = frozenset(exclude)
    lines = list(
        _recursively_make_command_docs(
            command=command,
            prog_name=program_name,
            parent_ctx=None,
            header_depth=header_depth,
            style=style,
            current_depth=0,
            max_depth=depth,
            exclude_set=exclude_set,
            show_hidden=show_hidden,
            list_subcommands=list_subcommands,
            remove_ascii_art=remove_ascii_art,
            full_command_path=full_command_path,
            command_path=program_name,
        )
    )
    # Collapse consecutive blank lines to a single blank line.
    deduped: list[str] = []
    for line in lines:
        if line == "" and deduped and deduped[-1] == "":  # NOQA: PLC1901
            continue
        deduped.append(line)
    return "\n".join(deduped) + "\n"


def _recursively_make_command_docs(
    command: click.BaseCommand,
    prog_name: str,
    parent_ctx: click.Context | None,
    header_depth: int,
    style: str,
    current_depth: int,
    max_depth: int | None,
    exclude_set: frozenset[str],
    show_hidden: bool,
    list_subcommands: bool,
    remove_ascii_art: bool,
    full_command_path: bool,
    command_path: str,
) -> Iterator[str]:
    """Yield Markdown lines for a command and its subcommands (depth-first)."""
    if getattr(command, "hidden", False) and not show_hidden:
        return

    ctx = command.make_context(prog_name, [], parent=parent_ctx, resilient_parsing=True)

    yield from _make_title(ctx, header_depth, full_command_path)
    yield from _make_description(ctx, remove_ascii_art)
    yield from _make_usage(ctx)
    yield from _make_options(ctx, style, show_hidden)

    if max_depth is not None and current_depth >= max_depth:
        return

    subcommands = _get_subcommands(command, ctx)
    if not subcommands:
        return

    subcommands.sort(key=lambda cmd: cmd.name or "")

    if list_subcommands and current_depth == 0:
        yield ""
        yield from _make_subcommands_toc(subcommands, ctx, show_hidden, full_command_path)

    for subcmd in subcommands:
        sub_name = subcmd.name or ""
        sub_path = f"{command_path}.{sub_name}"
        if sub_path in exclude_set:
            continue
        yield ""
        yield from _recursively_make_command_docs(
            command=subcmd,
            prog_name=sub_name,
            parent_ctx=ctx,
            header_depth=header_depth + 1,
            style=style,
            current_depth=current_depth + 1,
            max_depth=max_depth,
            exclude_set=exclude_set,
            show_hidden=show_hidden,
            list_subcommands=list_subcommands,
            remove_ascii_art=remove_ascii_art,
            full_command_path=full_command_path,
            command_path=sub_path,
        )


def _get_subcommands(command: click.BaseCommand, ctx: click.Context) -> list[click.BaseCommand]:
    """Return direct subcommands of a group command."""
    commands: dict = getattr(command, "commands", {})
    if commands:
        return list(commands.values())
    if isinstance(command, click.Group):
        result = []
        for name in command.list_commands(ctx):
            subcmd = command.get_command(ctx, name)
            if subcmd is not None:
                result.append(subcmd)
        return result
    return []


def _slugify(text: str) -> str:
    """Convert *text* to a GitHub-compatible anchor slug."""
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    return text.strip("-")


def _make_subcommands_toc(
    subcommands: list[click.BaseCommand],
    parent_ctx: click.Context,
    show_hidden: bool,
    full_command_path: bool,
) -> Iterator[str]:
    """Yield a bulleted TOC of direct subcommands with anchor links."""
    yield "**Subcommands:**"
    yield ""
    for cmd in subcommands:
        if getattr(cmd, "hidden", False) and not show_hidden:
            continue
        cmd_name = cmd.name or ""
        header_text = f"{parent_ctx.command_path} {cmd_name}" if full_command_path else cmd_name
        anchor = _slugify(header_text)
        short_help = _get_short_help(cmd)
        if short_help:
            yield f"- [{cmd_name}](#{anchor}): {short_help}"
        else:
            yield f"- [{cmd_name}](#{anchor})"
    yield ""


def _get_short_help(command: click.BaseCommand) -> str:
    """Return the first line of a command's help text (before \\f or \\n)."""
    help_text = getattr(command, "help", None) or getattr(command, "short_help", None) or ""
    help_text = inspect.cleandoc(help_text)
    help_text = help_text.partition("\f")[0]
    return help_text.splitlines()[0].strip() if help_text.strip() else ""


def _make_title(
    ctx: click.Context,
    header_depth: int = 1,
    full_command_path: bool = False,
) -> Iterator[str]:
    """Yield the command title as a Markdown heading at the given depth."""
    text = ctx.command_path if full_command_path else ctx.info_name
    yield f"{'#' * header_depth} {text}"
    yield ""


def _make_description(ctx: click.Context, remove_ascii_art: bool = False) -> Iterator[str]:
    """
    Yield help text lines, truncating at ``\\f``.

    Generates an iterator that provides a processed description text for a given Click command context. If
    `remove_ascii_art` is set to True, ASCII art blocks (delimited by the `\b` marker and a subsequent blank
    line) are excluded from the output.

    Args:
        ctx: The context of the Click command containing usage information or help text.
        remove_ascii_art: A flag to indicate whether ASCII art blocks should be removed
            from the processed output. It strips the ``\\b``-prefixed block (from the opening ``\\b`` line up to and
            including the next blank line).Defaults to False.

    Yields:
        str: Processed lines from the command's help text, optionally excluding ASCII art.
    """
    help_text = ctx.command.help or ctx.command.short_help
    if not help_text:
        return
    help_text = inspect.cleandoc(help_text)
    help_text = help_text.partition("\f")[0]

    if not remove_ascii_art:
        yield from help_text.splitlines()
        yield ""
        return

    # Strip the \b block: from first \b line through the next blank line.
    in_ascii_art = False
    for i, line in enumerate(help_text.splitlines()):
        if not in_ascii_art:
            if i == 0 and line.strip() == "\b":
                in_ascii_art = True
                continue
            yield line
        else:
            if not line.strip():
                in_ascii_art = False  # blank line ends the block; skip it
            # else: skip this ascii art line
    yield ""


def _make_usage(ctx: click.Context) -> Iterator[str]:
    """
    Yield a fenced-code usage block.

    This function utilizes the `click` library's context object to create a well-formatted usage message for
    a command, including its command path and usage details. The output is formatted with Markdown, rendering as a
    highlighted code block for easy display in documentation or CLI output.

    Args:
        ctx: The context provided by the `click` library, which contains information about the current command and
            its configurations.

    Yields:
        str: Formatted lines of the usage message, including Markdown elements for code highlighting and spacing.
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


def _make_options(ctx: click.Context, style: str = "plain", show_hidden: bool = False) -> Iterator[str]:
    """Dispatch to the appropriate options renderer."""
    if style == "table":
        yield from _make_options_table(ctx, show_hidden)
    else:
        yield from _make_options_plain(ctx, show_hidden)


@contextmanager
def _unhide_options(ctx: click.Context) -> Iterator[None]:
    """Temporarily unhide all hidden options on the command."""
    hidden_opts = [p for p in ctx.command.params if isinstance(p, click.Option) and p.hidden]
    try:
        for opt in hidden_opts:
            opt.hidden = False
        yield
    finally:
        for opt in hidden_opts:
            opt.hidden = True


def _make_options_plain(ctx: click.Context, show_hidden: bool = False) -> Iterator[str]:
    """Yield options as a fenced preformatted block from Click's own formatter.

    Help text is truncated at ``\\f`` before being passed to the formatter.
    """
    with ExitStack() as stack:
        if show_hidden:
            stack.enter_context(_unhide_options(ctx))

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


def _make_options_table(ctx: click.Context, show_hidden: bool = False) -> Iterator[str]:
    """Yield options as a Markdown table with Name, Type, and Description columns."""
    options = [
        p
        for p in ctx.command.params
        if isinstance(p, click.Option) and not _is_help_option(p) and (show_hidden or not p.hidden)
    ]
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
    """
    Render an IntRange or FloatRange as a bounds expression like ``0<=x<=10``.

    Generates a string representation of a numeric range based on the given
    parameter type. The range format includes minimum and maximum boundaries
    with appropriate open or closed intervals, along with the midpoint notation
    'x'. This utility function is specifically designed for Click's IntRange
    or FloatRange parameter types.

    Args:
        param_type: The range object defining the minimum and maximum bounds,
            as well as whether the intervals are open or closed.

    Returns:
        A formatted range string representing the numeric bounds and interval behavior.
    """
    min_op = "<" if getattr(param_type, "min_open", False) else "<="
    max_op = "<" if getattr(param_type, "max_open", False) else "<="
    parts = []
    if param_type.min is not None:
        parts.append(f"{param_type.min}{min_op}")
    parts.append("x")
    if param_type.max is not None:
        parts.append(f"{max_op}{param_type.max}")
    return "".join(parts)
