"""Unit tests for click_docs.config."""

from pathlib import Path

import pytest

from click_docs.config import find_config


class TestFindConfig:
    def test_returns_click_docs_section(self, tmp_path):
        """Returns dict from [tool.click-docs] when pyproject.toml exists in start dir."""
        (tmp_path / "pyproject.toml").write_text('[tool.click-docs]\nheader-depth = 2\nstyle = "table"\n')
        result = find_config(start=tmp_path)
        assert result == {"header-depth": 2, "style": "table"}

    def test_returns_empty_dict_when_no_pyproject_toml(self, tmp_path):
        """Returns empty dict when no pyproject.toml exists anywhere in the tree."""
        result = find_config(start=tmp_path)
        assert result == {}

    def test_finds_config_in_parent_directory(self, tmp_path):
        """Finds pyproject.toml in a parent directory when absent from start dir."""
        child = tmp_path / "subdir"
        child.mkdir()
        (tmp_path / "pyproject.toml").write_text("[tool.click-docs]\nheader-depth = 3\n")
        result = find_config(start=child)
        assert result == {"header-depth": 3}

    def test_returns_empty_dict_when_no_click_docs_section(self, tmp_path):
        """Returns empty dict when pyproject.toml exists but lacks [tool.click-docs]."""
        (tmp_path / "pyproject.toml").write_text('[tool.other]\nfoo = "bar"\n')
        result = find_config(start=tmp_path)
        assert result == {}

    def test_excludes_parsed_as_list(self, tmp_path):
        """exclude key is returned as a list when specified as TOML array."""
        (tmp_path / "pyproject.toml").write_text('[tool.click-docs]\nexclude = ["root.admin", "root.hello"]\n')
        result = find_config(start=tmp_path)
        assert result == {"exclude": ["root.admin", "root.hello"]}

    def test_defaults_to_cwd(self, tmp_path, monkeypatch):
        """When start is not provided, uses current working directory."""
        (tmp_path / "pyproject.toml").write_text("[tool.click-docs]\nheader-depth = 4\n")
        monkeypatch.chdir(tmp_path)
        result = find_config()
        assert result == {"header-depth": 4}
