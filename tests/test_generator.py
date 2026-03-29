"""Tests for click_docs.generator module."""

from pathlib import Path

import click
import pytest

from click_docs.generator import generate_docs

EXPECTED_DIR = Path(__file__).parent / "app"

# ---------------------------------------------------------------------------
# Phase 3 fixture commands (mirrors tests/app/cli.py for isolation)
# ---------------------------------------------------------------------------


@click.command(name="reset")
@click.option("--force", is_flag=True, help="Force the reset.")
def _reset(force):
    """Reset the system to defaults."""


@click.command(name="secret", hidden=True)
def _secret():
    """Top-secret command."""


@click.command(name="status")
@click.option("--verbose", is_flag=True, hidden=True, help="Enable verbose output.")
def _status(verbose):
    """Check system status."""


@click.group(name="admin")
def _admin():
    """Admin commands."""


_admin.add_command(_reset)
_admin.add_command(_secret)
_admin.add_command(_status)


@click.command(name="hello")
@click.option("--name", required=True, help="The person to greet.")
def _hello(name):
    """Simple program that greets NAME."""


@click.group(name="root")
def _root():
    """Root command with subgroups."""


_root.add_command(_admin)
_root.add_command(_hello)


@click.command(name="ascii-art")
def _ascii_art():
    """\b
    ===  ASCII ART  ===

    Regular description after the art."""


@click.command()
@click.option("--count", default=1, help="Number of greetings.")
@click.option("--name", required=True, help="The person to greet.")
def hello(count, name):
    """Simple program that greets NAME for a total of COUNT times."""


@click.group()
def cli():
    """Main entrypoint for this test app."""


cli.add_command(hello)


class TestGenerateDocs:
    def test_simple_command_matches_snapshot(self):
        """A simple command generates the expected Markdown snapshot."""
        expected = (EXPECTED_DIR / "expected_hello.md").read_text()
        result = generate_docs(hello, program_name="hello")
        assert result == expected

    def test_group_command_matches_snapshot(self):
        """A group command generates the expected Markdown snapshot (root only for phase 1)."""
        expected = (EXPECTED_DIR / "expected_cli.md").read_text()
        result = generate_docs(cli, program_name="cli")
        assert result == expected

    def test_uses_command_name_as_default_program_name(self):
        """When program_name is omitted, the command's own name is used."""
        result = generate_docs(hello)
        assert result.startswith("# hello\n")

    def test_custom_program_name_appears_in_output(self):
        """A custom program_name replaces the command name in the heading and usage."""
        result = generate_docs(hello, program_name="greet")
        assert result.startswith("# greet\n")
        assert "greet [OPTIONS]" in result

    def test_output_is_deterministic(self):
        """Calling generate_docs twice with the same inputs produces identical output."""
        result1 = generate_docs(hello, program_name="hello")
        result2 = generate_docs(hello, program_name="hello")
        assert result1 == result2

    def test_command_with_no_description_omits_description_section(self):
        """A command with no docstring omits the description section."""

        @click.command()
        def no_desc():
            pass

        result = generate_docs(no_desc, program_name="no-desc")
        assert "**Usage:**" in result
        lines = result.splitlines()
        assert lines[0] == "# no-desc"
        assert lines[1] == ""
        assert lines[2] == "**Usage:**"


@click.command()
@click.option("--fmt", type=click.Choice(["json", "yaml", "toml"]), help="Output format.")
@click.option("--level", type=click.IntRange(0, 10), help="Log level.")
@click.option("--ratio", type=click.FloatRange(0.0, 1.0), help="Ratio value.")
@click.option("--date", type=click.DateTime(["%Y-%m-%d", "%d/%m/%Y"]), help="A date.")
@click.option("--infile", type=click.File("r"), help="Input file.")
@click.option("--msg", help="Message.\f\nHidden text.")
def special_types_cmd(fmt, level, ratio, date, infile, msg):
    """Command with various special types."""


class TestHeaderDepth:
    def test_depth_1_produces_single_hash(self):
        result = generate_docs(hello, program_name="hello", header_depth=1)
        assert result.startswith("# hello\n")

    def test_depth_2_produces_double_hash(self):
        result = generate_docs(hello, program_name="hello", header_depth=2)
        assert result.startswith("## hello\n")

    def test_depth_3_produces_triple_hash(self):
        result = generate_docs(hello, program_name="hello", header_depth=3)
        assert result.startswith("### hello\n")

    def test_depth_6_produces_six_hashes(self):
        result = generate_docs(hello, program_name="hello", header_depth=6)
        assert result.startswith("###### hello\n")

    def test_depth_default_is_1(self):
        result = generate_docs(hello, program_name="hello")
        assert result.startswith("# hello\n")


class TestStyleTable:
    def test_produces_markdown_table_header(self):
        result = generate_docs(hello, program_name="hello", style="table")
        assert "| Name | Type | Description |" in result

    def test_table_separator_row_present(self):
        result = generate_docs(hello, program_name="hello", style="table")
        assert "| --- | --- | --- |" in result

    def test_omits_help_option(self):
        result = generate_docs(hello, program_name="hello", style="table")
        assert "--help" not in result

    def test_shows_option_names(self):
        result = generate_docs(hello, program_name="hello", style="table")
        assert "--count" in result
        assert "--name" in result

    def test_plain_style_still_produces_code_block(self):
        result = generate_docs(hello, program_name="hello", style="plain")
        assert "```text" in result
        assert "| Name | Type | Description |" not in result

    def test_choice_type_shows_constraint(self):
        result = generate_docs(special_types_cmd, style="table")
        assert "one of: json, yaml, toml" in result

    def test_intrange_shows_bounds(self):
        result = generate_docs(special_types_cmd, style="table")
        assert "0<=x<=10" in result

    def test_floatrange_shows_bounds(self):
        result = generate_docs(special_types_cmd, style="table")
        assert "0.0<=x<=1.0" in result

    def test_datetime_shows_formats(self):
        result = generate_docs(special_types_cmd, style="table")
        assert "%Y-%m-%d" in result
        assert "%d/%m/%Y" in result

    def test_file_shows_mode(self):
        result = generate_docs(special_types_cmd, style="table")
        assert "file (r)" in result

    def test_ff_escape_truncated_in_table(self):
        result = generate_docs(special_types_cmd, style="table")
        assert "Hidden text" not in result
        assert "Message." in result

    def test_snapshot_table(self):
        expected = (EXPECTED_DIR / "expected_special_types_table.md").read_text()
        result = generate_docs(special_types_cmd, program_name="special-types", style="table")
        assert result == expected

    def test_snapshot_plain(self):
        expected = (EXPECTED_DIR / "expected_special_types_plain.md").read_text()
        result = generate_docs(special_types_cmd, program_name="special-types", style="plain")
        assert result == expected


# ---------------------------------------------------------------------------
# Phase 3 tests
# ---------------------------------------------------------------------------


class TestGroupRecursion:
    def test_group_includes_subcommand_docs(self):
        result = generate_docs(_root, program_name="root")
        assert "# root" in result
        assert "## admin" in result
        assert "## hello" in result

    def test_subcommand_docs_include_title(self):
        result = generate_docs(_root, program_name="root")
        assert "Admin commands." in result
        assert "Simple program that greets NAME." in result

    def test_subcommand_usage_uses_full_path(self):
        result = generate_docs(_root, program_name="root")
        assert "root admin" in result
        assert "root hello" in result

    def test_nested_group_recurses_to_leaves(self):
        result = generate_docs(_root, program_name="root")
        assert "### reset" in result
        assert "### status" in result

    def test_snapshot_recursive(self):
        expected = (EXPECTED_DIR / "expected_root_recursive.md").read_text()
        result = generate_docs(_root, program_name="root")
        assert result == expected


class TestDepthLimiting:
    def test_depth_0_produces_root_only(self):
        result = generate_docs(_root, program_name="root", depth=0)
        assert "# root" in result
        assert "## admin" not in result
        assert "## hello" not in result

    def test_depth_1_includes_direct_children(self):
        result = generate_docs(_root, program_name="root", depth=1)
        assert "# root" in result
        assert "## admin" in result
        assert "## hello" in result

    def test_depth_1_excludes_grandchildren(self):
        result = generate_docs(_root, program_name="root", depth=1)
        assert "### reset" not in result
        assert "### status" not in result

    def test_depth_none_is_unlimited(self):
        result = generate_docs(_root, program_name="root", depth=None)
        assert "### reset" in result
        assert "### status" in result

    def test_snapshot_depth_0(self):
        expected = (EXPECTED_DIR / "expected_root_depth_0.md").read_text()
        result = generate_docs(_root, program_name="root", depth=0)
        assert result == expected

    def test_snapshot_depth_1(self):
        expected = (EXPECTED_DIR / "expected_root_depth_1.md").read_text()
        result = generate_docs(_root, program_name="root", depth=1)
        assert result == expected


class TestExclusion:
    def test_exclude_skips_command_and_subtree(self):
        result = generate_docs(_root, program_name="root", exclude=("root.admin",))
        assert "## admin" not in result
        assert "### reset" not in result

    def test_excluded_sibling_still_present(self):
        result = generate_docs(_root, program_name="root", exclude=("root.admin",))
        assert "## hello" in result

    def test_exclude_leaf_command(self):
        result = generate_docs(_root, program_name="root", exclude=("root.admin.reset",))
        assert "## admin" in result
        assert "### reset" not in result
        assert "### status" in result

    def test_multiple_excludes(self):
        result = generate_docs(_root, program_name="root", exclude=("root.admin", "root.hello"))
        assert "## admin" not in result
        assert "## hello" not in result

    def test_snapshot_exclude_admin(self):
        expected = (EXPECTED_DIR / "expected_root_exclude_admin.md").read_text()
        result = generate_docs(_root, program_name="root", exclude=("root.admin",))
        assert result == expected


class TestHiddenCommands:
    def test_hidden_command_omitted_by_default(self):
        result = generate_docs(_admin, program_name="admin")
        assert "secret" not in result

    def test_show_hidden_includes_hidden_command(self):
        result = generate_docs(_admin, program_name="admin", show_hidden=True)
        assert "secret" in result

    def test_hidden_option_omitted_by_default(self):
        result = generate_docs(_admin, program_name="admin")
        # status subcommand has --verbose hidden option
        assert "--verbose" not in result

    def test_show_hidden_includes_hidden_option(self):
        result = generate_docs(_admin, program_name="admin", show_hidden=True)
        assert "--verbose" in result

    def test_snapshot_show_hidden(self):
        expected = (EXPECTED_DIR / "expected_admin_show_hidden.md").read_text()
        result = generate_docs(_admin, program_name="admin", show_hidden=True)
        assert result == expected


class TestListSubcommands:
    def test_list_subcommands_prepends_toc(self):
        result = generate_docs(_root, program_name="root", list_subcommands=True)
        assert "**Subcommands:**" in result

    def test_toc_contains_links(self):
        result = generate_docs(_root, program_name="root", list_subcommands=True)
        assert "[admin](#admin)" in result
        assert "[hello](#hello)" in result

    def test_toc_links_include_short_help(self):
        result = generate_docs(_root, program_name="root", list_subcommands=True)
        assert "Admin commands." in result

    def test_toc_hidden_commands_excluded_by_default(self):
        result = generate_docs(_admin, program_name="admin", list_subcommands=True)
        assert "[secret]" not in result

    def test_toc_appears_before_subcommand_sections(self):
        result = generate_docs(_root, program_name="root", list_subcommands=True)
        toc_pos = result.index("**Subcommands:**")
        admin_pos = result.index("## admin")
        assert toc_pos < admin_pos

    def test_toc_only_at_root_level(self):
        # Admin subgroup should NOT get its own TOC listing
        result = generate_docs(_root, program_name="root", list_subcommands=True)
        assert result.count("**Subcommands:**") == 1

    def test_full_command_path_toc_uses_path_anchor(self):
        result = generate_docs(_root, program_name="root", list_subcommands=True, full_command_path=True)
        assert "[admin](#root-admin)" in result
        assert "[hello](#root-hello)" in result

    def test_snapshot_list_subcommands(self):
        expected = (EXPECTED_DIR / "expected_root_list_subcommands.md").read_text()
        result = generate_docs(_root, program_name="root", list_subcommands=True)
        assert result == expected


class TestFullCommandPath:
    def test_subcommand_headers_use_full_path(self):
        result = generate_docs(_root, program_name="root", full_command_path=True)
        assert "## root admin" in result
        assert "## root hello" in result

    def test_nested_subcommand_header_uses_full_path(self):
        result = generate_docs(_root, program_name="root", full_command_path=True)
        assert "### root admin reset" in result

    def test_root_header_unchanged(self):
        result = generate_docs(_root, program_name="root", full_command_path=True)
        assert result.startswith("# root\n")


class TestRemoveAsciiArt:
    def test_removes_backslash_b_block(self):
        result = generate_docs(_ascii_art, program_name="ascii-art", remove_ascii_art=True)
        assert "===" not in result
        assert "ASCII ART" not in result

    def test_preserves_text_after_blank_line(self):
        result = generate_docs(_ascii_art, program_name="ascii-art", remove_ascii_art=True)
        assert "Regular description after the art." in result

    def test_without_flag_preserves_backslash_b_content(self):
        result = generate_docs(_ascii_art, program_name="ascii-art", remove_ascii_art=False)
        assert "ASCII ART" in result

    def test_snapshot_remove_ascii_art(self):
        expected = (EXPECTED_DIR / "expected_ascii_art_removed.md").read_text()
        result = generate_docs(_ascii_art, program_name="ascii-art", remove_ascii_art=True)
        assert result == expected
