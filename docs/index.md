---
title: Click Docs
summary: Generate Markdown documentation for your Click application
date: 2026-03-29T12:43:32.559666+00:00
---

# Click Docs

> Generate Markdown documentation for your Click application

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

## What Next

Check out the [Tutorials](tutorials/index.md) or [Reference](reference/index.md) for more information.
Developers should check out the [Developer Guide](development.md) for even more detailed information
and advice on how to extend Click Docs.
