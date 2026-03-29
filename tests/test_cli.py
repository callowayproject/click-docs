"""Integration tests for the click-docs CLI."""

from pathlib import Path

import pytest
from click.testing import CliRunner

from click_docs.cli import cli

FIXTURE_APP = "tests/app/cli.py"
EXPECTED_DIR = Path(__file__).parent / "app"


@pytest.fixture
def runner():
    return CliRunner()


class TestCliStdout:
    def test_prints_markdown_to_stdout(self, runner):
        """Running with a valid module path prints Markdown to stdout."""
        result = runner.invoke(cli, [FIXTURE_APP])
        assert result.exit_code == 0
        assert "# cli" in result.output
        assert "**Usage:**" in result.output

    def test_default_command_name_is_cli(self, runner):
        """Without --command-name, the 'cli' attribute is loaded by default."""
        result = runner.invoke(cli, [FIXTURE_APP])
        assert result.exit_code == 0
        assert "# cli" in result.output

    def test_explicit_command_name(self, runner):
        """--command-name selects a specific attribute from the module."""
        result = runner.invoke(cli, [FIXTURE_APP, "--command-name", "hello"])
        assert result.exit_code == 0
        assert "# hello" in result.output

    def test_dotted_command_name(self, runner):
        """--command-name accepts a dotted path to a nested attribute."""
        result = runner.invoke(cli, [FIXTURE_APP, "--command-name", "NestedCommands.root"])
        assert result.exit_code == 0
        assert "# cli" in result.output


class TestCliFileOutput:
    def test_writes_to_output_file(self, runner, tmp_path):
        """--output writes Markdown to the specified file."""
        out_file = tmp_path / "cli.md"
        result = runner.invoke(cli, [FIXTURE_APP, "--output", str(out_file)])
        assert result.exit_code == 0
        assert out_file.exists()
        content = out_file.read_text()
        assert "# cli" in content

    def test_overwrites_existing_file_silently(self, runner, tmp_path):
        """--output silently overwrites a file that already exists."""
        out_file = tmp_path / "existing.md"
        out_file.write_text("old content")
        result = runner.invoke(cli, [FIXTURE_APP, "--output", str(out_file)])
        assert result.exit_code == 0
        assert out_file.read_text() != "old content"

    def test_output_dir_does_not_exist_exits_with_error(self, runner, tmp_path):
        """--output whose parent directory does not exist exits with code 1."""
        out_file = tmp_path / "nonexistent_dir" / "cli.md"
        result = runner.invoke(cli, [FIXTURE_APP, "--output", str(out_file)])
        assert result.exit_code == 1
        assert "directory" in result.output.lower() or "directory" in (result.stderr or "").lower()


class TestCliErrors:
    def test_bad_module_path_exits_with_code_1(self, runner):
        """A non-existent module path exits with code 1 and a message on stderr."""
        result = runner.invoke(cli, ["nonexistent/path.py"])
        assert result.exit_code == 1

    def test_bad_module_path_has_descriptive_message(self, runner):
        """A non-existent module path shows a human-readable error message."""
        result = runner.invoke(cli, ["nonexistent/path.py"])
        assert "nonexistent/path.py" in result.output or "nonexistent/path.py" in (result.stderr or "")

    def test_missing_attribute_exits_with_code_1(self, runner):
        """A missing command attribute exits with code 1."""
        result = runner.invoke(cli, [FIXTURE_APP, "--command-name", "does_not_exist"])
        assert result.exit_code == 1

    def test_non_click_attribute_exits_with_code_1(self, runner):
        """A non-Click attribute exits with code 1."""
        result = runner.invoke(cli, [FIXTURE_APP, "--command-name", "NOT_A_COMMAND"])
        assert result.exit_code == 1

    def test_no_traceback_shown_on_error(self, runner):
        """Error output does not contain a Python traceback."""
        result = runner.invoke(cli, ["nonexistent/path.py"])
        assert "Traceback" not in result.output
        assert "Traceback" not in (result.stderr or "")


class TestCliFormattingOptions:
    def test_program_name_overrides_heading(self, runner):
        result = runner.invoke(cli, [FIXTURE_APP, "--program-name", "myapp"])
        assert result.exit_code == 0
        assert "# myapp" in result.output

    def test_program_name_appears_in_usage(self, runner):
        result = runner.invoke(cli, [FIXTURE_APP, "--program-name", "myapp"])
        assert result.exit_code == 0
        assert "myapp" in result.output

    def test_header_depth_2_produces_double_hash(self, runner):
        result = runner.invoke(cli, [FIXTURE_APP, "--header-depth", "2"])
        assert result.exit_code == 0
        assert "## cli" in result.output

    def test_header_depth_default_is_1(self, runner):
        result = runner.invoke(cli, [FIXTURE_APP])
        assert result.exit_code == 0
        assert "# cli" in result.output

    def test_style_table_produces_table(self, runner):
        result = runner.invoke(cli, [FIXTURE_APP, "--command-name", "hello", "--style", "table"])
        assert result.exit_code == 0
        assert "| Name | Type | Description |" in result.output

    def test_style_plain_produces_code_block(self, runner):
        result = runner.invoke(cli, [FIXTURE_APP, "--style", "plain"])
        assert result.exit_code == 0
        assert "```text" in result.output

    def test_style_invalid_exits_with_error(self, runner):
        result = runner.invoke(cli, [FIXTURE_APP, "--style", "invalid"])
        assert result.exit_code != 0

    def test_style_table_omits_help_option(self, runner):
        result = runner.invoke(cli, [FIXTURE_APP, "--command-name", "special_types", "--style", "table"])
        assert result.exit_code == 0
        assert "| Name | Type | Description |" in result.output
        assert "--help" not in result.output
