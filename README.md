# click-docs

Generate Markdown documentation from your Click application — automatically, from source, with no manual editing required.

[![PyPI version](https://img.shields.io/pypi/v/click-docs)](https://pypi.org/project/click-docs/)
[![Python versions](https://img.shields.io/pypi/pyversions/click-docs)](https://pypi.org/project/click-docs/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![CI](https://img.shields.io/github/actions/workflow/status/callowayproject/click-docs/test.yaml)](https://github.com/callowayproject/click-docs/actions)

## About

Click applications document themselves — click-docs reads that information and turns it into clean Markdown. Point it at a Python file, get a complete reference page: usage lines, options tables, nested subcommands, the works.

It introspects Click objects directly and never executes your application, so there are no side effects and the output is always in sync with your source.

## Features

- **Zero-execution introspection** — reads Click objects, never runs your app
- **Nested command support** — recursively documents subcommands with configurable depth
- **Two option styles** — `plain` (preformatted text) or `table` (Markdown table)
- **Configurable via `pyproject.toml`** — set defaults once in `[tool.click-docs]`
- **Subcommand TOC** — optional bulleted table of contents at the top
- **Filtering** — exclude specific commands, skip hidden commands, strip ASCII art blocks

## Installation

```console
$ pip install click-docs
```

Or with `uv`:

```console
$ uv add click-docs
```

**Requirements:** Python 3.10+, Click 8.1+

## Quick start

Given a file `deployer.py` containing a Click application:

```console
$ click-docs deployer.py --program-name deployer --output docs/cli-reference.md
```

That's it. `docs/cli-reference.md` now contains the full Markdown reference for every command and option.

## Common options

| Option                 | Description                                   |
|------------------------|-----------------------------------------------|
| `--program-name TEXT`  | Display name in headings and usage lines      |
| `--output FILE`        | Write to file instead of stdout               |
| `--style plain\|table` | Options rendering style                       |
| `--depth N`            | Max subcommand depth (0 = root only)          |
| `--exclude PATH`       | Exclude a command by dotted path (repeatable) |
| `--list-subcommands`   | Prepend a TOC of subcommands                  |
| `--remove-ascii-art`   | Strip `\b`-prefixed ASCII art blocks          |

Run `click-docs --help` for the full list.

## Configure defaults in pyproject.toml

Set project-wide defaults so you don't repeat flags on every run:

```toml
[tool.click-docs]
program-name = "my-tool"
style = "table"
list-subcommands = true
remove-ascii-art = true
output = "docs/cli-reference.md"
```

## Documentation

Full documentation, tutorials, and API reference: [callowayproject.github.io/click_docs](https://callowayproject.github.io/click_docs)

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development setup

```console
$ git clone https://github.com/callowayproject/click-docs.git
$ cd click-docs
$ uv sync
$ uv run pytest
```

## License

click-docs is licensed under the Apache 2.0 license. See the [`LICENSE`](LICENSE) file for details.
