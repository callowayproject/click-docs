"""Tests for click_docs.generator module."""

from pathlib import Path

import click
import pytest

from click_docs.generator import generate_docs

EXPECTED_DIR = Path(__file__).parent / "app"


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
