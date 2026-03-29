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
