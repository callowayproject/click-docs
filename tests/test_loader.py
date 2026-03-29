"""Tests for click_docs.loader module."""

import pytest

from click_docs.loader import LoadError, load_command


FIXTURE_APP = "tests/app/cli.py"


class TestLoadCommand:
    def test_valid_path_and_default_command_name_returns_click_command(self):
        """Loading a valid module with the default 'cli' attribute returns a Click command."""
        import click

        cmd = load_command(FIXTURE_APP)
        assert isinstance(cmd, click.Command)
        assert cmd.name == "cli"

    def test_valid_path_and_explicit_command_name_returns_click_command(self):
        """Loading a valid module with an explicit command name returns the correct command."""
        import click

        cmd = load_command(FIXTURE_APP, command_name="hello")
        assert isinstance(cmd, click.Command)
        assert cmd.name == "hello"

    def test_dotted_command_name_resolves_nested_attribute(self):
        """A dotted command name like 'NestedCommands.root' resolves the nested attribute."""
        import click

        cmd = load_command(FIXTURE_APP, command_name="NestedCommands.root")
        assert isinstance(cmd, click.Command)
        assert cmd.name == "cli"

    def test_bad_module_path_raises_load_error(self):
        """A non-existent file path raises LoadError with a descriptive message."""
        with pytest.raises(LoadError, match="does not exist"):
            load_command("nonexistent/path/to/module.py")

    def test_missing_attribute_raises_load_error(self):
        """A missing attribute name on the module raises LoadError."""
        with pytest.raises(LoadError, match="has no attribute"):
            load_command(FIXTURE_APP, command_name="nonexistent_command")

    def test_dotted_path_missing_intermediate_raises_load_error(self):
        """A dotted path with a missing intermediate attribute raises LoadError."""
        with pytest.raises(LoadError, match="has no attribute"):
            load_command(FIXTURE_APP, command_name="missing.root")

    def test_non_click_attribute_raises_load_error(self):
        """An attribute that is not a Click command raises LoadError."""
        with pytest.raises(LoadError, match="not a Click command"):
            load_command(FIXTURE_APP, command_name="NOT_A_COMMAND")
