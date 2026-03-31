---
title: Documenting a Real-World CLI
summary: Use click-docs' full feature set to document a complex CLI with nested subgroups, hidden commands, special option types, and persistent configuration.
date: 2026-03-30T00:00:00+00:00
---

# Documenting a Real-World CLI

[Tutorial 1](first-cli-documentation.md) covered the basics: install, point at a file, get Markdown. Real CLIs are more complicated. They have nested subgroups, admin commands you don't want in the public docs, options with rich types like ranges and choices, and sometimes a splash of ASCII art in the help text.

This tutorial walks through all of that using an extended version of the `deployer` tool from Tutorial 1.

**What you'll build:** A fully documented reference for a multi-group CLI, configured entirely through `pyproject.toml` so you never need to type the same flags twice.

!!! note "Prerequisites"

    Complete [Tutorial 1](first-cli-documentation.md) first, or at minimum have click-docs installed (`pip install click-docs`).

---

## 1. The extended deployer

Replace the contents of `deployer.py` with this expanded version. It adds an ASCII art banner, a `logs` command with richer option types, a `config` subgroup, and a hidden `admin` subgroup:

```python title="deployer.py"
import click


@click.group()
def cli():
    """\b
     ____             _
    |  _ \  ___ _ __ | | ___  _   _  ___ _ __
    | | | |/ _ \ '_ \| |/ _ \| | | |/ _ \ '__|
    | |_| |  __/ |_) | | (_) | |_| |  __/ |
    |____/ \___| .__/|_|\___/ \__, |\___|_|
               |_|            |___/

    A tool for deploying and managing web applications.
    """


@cli.command()
@click.argument("app_name")
@click.option(
    "--env", "-e",
    default="staging",
    show_default=True,
    type=click.Choice(["staging", "production"]),
    help="Target deployment environment.",
)
@click.option(
    "--version", "-v",
    default="latest",
    show_default=True,
    help="Application version tag to deploy.",
)
@click.option("--dry-run", is_flag=True, help="Preview the deployment without executing it.")
@click.option(
    "--workers",
    type=click.IntRange(1, 16),
    default=4,
    show_default=True,
    help="Number of parallel deployment workers.",
)
def deploy(app_name, env, version, dry_run, workers):
    """Deploy APP_NAME to the target environment."""
    click.echo(f"Deploying {app_name} ({version}) to {env} with {workers} workers...")


@cli.command()
@click.argument("app_name")
@click.option(
    "--env", "-e",
    required=True,
    type=click.Choice(["staging", "production"]),
    help="Environment to roll back.",
)
def rollback(app_name, env):
    """Roll back APP_NAME to its previous version."""
    click.echo(f"Rolling back {app_name} in {env}...")


@cli.command()
@click.argument("app_name")
@click.option(
    "--env", "-e",
    default="staging",
    show_default=True,
    type=click.Choice(["staging", "production"]),
    help="Environment to check status for.",
)
def status(app_name, env):
    """Check the deployment status of APP_NAME."""
    click.echo(f"Status for {app_name} in {env}: running")


@cli.command()
@click.argument("app_name")
@click.option(
    "--env", "-e",
    default="staging",
    show_default=True,
    type=click.Choice(["staging", "production"]),
    help="Environment to fetch logs from.",
)
@click.option(
    "--lines", "-n",
    type=click.IntRange(1, 1000),
    default=100,
    show_default=True,
    help="Number of log lines to retrieve.",
)
@click.option(
    "--format", "fmt",
    type=click.Choice(["text", "json", "structured"]),
    default="text",
    show_default=True,
    help="Output format for log entries.",
)
@click.option("--follow", "-f", is_flag=True, help="Stream logs in real time.")
@click.option("--debug-token", hidden=True, help="Internal token for debug mode.")
def logs(app_name, env, lines, fmt, follow, debug_token):
    """Stream or display recent logs for APP_NAME."""
    click.echo(f"Fetching {lines} lines from {app_name} in {env}...")


@cli.group()
def config():
    """Manage per-environment application configuration."""


@config.command("set")
@click.argument("key")
@click.argument("value")
@click.option(
    "--env", "-e",
    default="staging",
    show_default=True,
    type=click.Choice(["staging", "production"]),
    help="Target environment for the config entry.",
)
def config_set(key, value, env):
    """Set configuration KEY to VALUE."""
    click.echo(f"Set {key}={value} in {env}")


@config.command("get")
@click.argument("key")
@click.option(
    "--env", "-e",
    default="staging",
    show_default=True,
    type=click.Choice(["staging", "production"]),
    help="Environment to read config from.",
)
def config_get(key, env):
    """Get the current value of configuration KEY."""
    click.echo(f"Getting {key} from {env}...")


@config.command("list")
@click.option(
    "--env", "-e",
    default="staging",
    show_default=True,
    type=click.Choice(["staging", "production"]),
    help="Environment to list config for.",
)
@click.option(
    "--format", "fmt",
    type=click.Choice(["table", "json", "env"]),
    default="table",
    show_default=True,
    help="Output format.",
)
def config_list(env, fmt):
    """List all configuration entries for the environment."""
    click.echo(f"Config for {env}...")


@cli.group(hidden=True)
def admin():
    """Internal admin commands. Not for regular users."""


@admin.command()
@click.option("--force", is_flag=True, help="Skip the confirmation prompt.")
def purge(force):
    """Purge all deployment history."""
    click.echo("Purging deployment history...")


@admin.command(hidden=True)
def nuke():
    """Irreversibly destroy all deployment data and configuration."""
    click.echo("Done.")
```

A few things worth noticing in this code:

- The root `cli` docstring starts with `\b`. That's how Click marks a no-wrap block — it's the conventional way to include ASCII art in help text.
- `logs` uses `click.IntRange(1, 1000)` and `click.Choice(...)` — richer types that click-docs knows how to render.
- `--debug-token` has `hidden=True`. It won't appear in the docs by default.
- The `admin` group itself has `hidden=True`. The entire subgroup and everything inside it is invisible unless you ask for it.

---

## 2. Run it and see what you have

Start with a plain run to get the baseline output:

```console
$ click-docs deployer.py --program-name deployer
```

You'll see the full recursive documentation — root group, then `config`, `deploy`, `logs`, `rollback`, `status` in alphabetical order, followed by `config`'s three subcommands (`get`, `list`, `set`). The `admin` group is nowhere to be found because it's hidden.

The default output works, but it has two rough edges we'll fix in this tutorial:

1. The root section opens with the raw ASCII art banner, which looks odd in Markdown.
2. The hidden `admin` group might be something you actually want in an internal reference.

Let's work through each feature.

---

## 3. Nested subgroups work automatically

No special flags needed for the `config` group. click-docs recurses into every subgroup it finds, incrementing the header level at each depth. In your output you'll see:

~~~markdown
## config

Manage per-environment application configuration.

**Usage:**

```text
deployer config [OPTIONS] COMMAND [ARGS]...
```

**Options:**

```text
  --help  Show this message and exit.
```

### get

Get the current value of configuration KEY.

...

### list

List all configuration entries for the environment.

...

### set

Set configuration KEY to VALUE.

...
~~~

`config` gets a level-2 heading, its subcommands get level-3. If `config` had its own nested groups, those would be level-4, and so on.

---

## 4. Limit documentation depth

Sometimes you don't want to document every level. Maybe `config`'s subcommands are simple enough that a single-paragraph description of the group is all users need, or you're generating a high-level overview for a README.

Use `--depth` to cap how deep the recursion goes. Depth is measured from the root:

| `--depth` value | What's documented |
| --- | --- |
| `0` | Root command only |
| `1` | Root + direct subcommands (no sub-subcommands) |
| `2` | Root + two levels deep |
| *(omitted)* | Unlimited |

A depth-0 run — just the root:

```console
$ click-docs deployer.py --program-name deployer --depth 0
```

~~~markdown
# deployer

 ____             _
|  _ \  ___ ...

A tool for deploying and managing web applications.

**Usage:**

```text
deployer [OPTIONS] COMMAND [ARGS]...
```

**Options:**

```text
  --help  Show this message and exit.
```
~~~

A depth-1 run — root and its direct subcommands, but not `config get`, `config list`, or `config set`:

```console
$ click-docs deployer.py --program-name deployer --depth 1
```

You'll see `config`, `deploy`, `logs`, `rollback`, and `status` with their own usage and options, but the `config` subcommands won't appear.

---

## 5. Exclude specific commands

`--depth` is a blunt instrument — it cuts the entire tree at a given level. If you want to exclude one specific branch while keeping everything else, use `--exclude`.

The argument is a dotted path from the root command name to the command you want to drop. The root command name in our file is `cli` (the Python function name), so to exclude the `config` group:

```console
$ click-docs deployer.py --program-name deployer --exclude cli.config
```

The `config` group and all three of its subcommands disappear from the output. Everything else remains.

You can pass `--exclude` multiple times to drop several branches:

```console
$ click-docs deployer.py --program-name deployer --exclude cli.config --exclude cli.rollback
```

!!! warning "Use the function name, not the program name"

    The dotted path uses the command's underlying name — the Python function name or the `name=` argument passed to the decorator — not the `--program-name` display override. Our root group function is called `cli`, so the path starts with `cli.`, not `deployer.`.

---

## 6. Reveal hidden commands and options

The `admin` group is marked `hidden=True`, so it's invisible in normal runs. The `--debug-token` option on `logs` is also hidden. To include them in your output, add `--show-hidden`:

```console
$ click-docs deployer.py --program-name deployer --show-hidden
```

The output now includes the `admin` section with `purge` and `nuke`, and the `--debug-token` option appears in the `logs` section:

~~~markdown
## admin

Internal admin commands. Not for regular users.

**Usage:**

```text
deployer admin [OPTIONS] COMMAND [ARGS]...
```

**Options:**

```text
  --help  Show this message and exit.
```

### nuke

Irreversibly destroy all deployment data and configuration.

...

### purge

Purge all deployment history.

...
~~~

!!! tip

    `--show-hidden` is ideal for generating an internal reference. You can maintain a single CLI definition and generate two documentation pages from it: a public one (without `--show-hidden`) and a private one (with it).

---

## 7. Switch to table style

By default, click-docs renders options as a formatted text block — exactly what you'd see if you ran your CLI with `--help`. This is the `plain` style.

The `table` style renders options as a Markdown table instead, which some documentation sites display more attractively and which makes complex type information easier to scan:

```console
$ click-docs deployer.py --program-name deployer --style table
```

Here's what the `logs` command's options look like in table style:

~~~markdown
## logs

Stream or display recent logs for APP_NAME.

**Usage:**

```text
deployer logs [OPTIONS] APP_NAME
```

**Options:**

| Name | Type | Description |
| --- | --- | --- |
| -e, --env | one of: staging, production | Environment to fetch logs from. |
| -n, --lines | 1<=x<=1000 | Number of log lines to retrieve. |
| --format | one of: text, json, structured | Output format for log entries. |
| --follow | BOOL | Stream logs in real time. |
~~~

Notice how `IntRange(1, 1000)` becomes `1<=x<=1000` and `Choice(["text", "json", "structured"])` becomes `one of: text, json, structured`. The table style has built-in rendering for Click's rich parameter types.

!!! note

    The `--help` option is always omitted from the table style — it's self-evident and would add noise to every single table.

---

## 8. Add a subcommand table of contents

For CLIs with many top-level subcommands, it helps to give readers a quick overview before they hit the detailed sections. `--list-subcommands` inserts a bulleted list of direct subcommands after the root command's options:

```console
$ click-docs deployer.py --program-name deployer --list-subcommands
```

~~~markdown
# deployer

...

**Options:**

```text
  --help  Show this message and exit.
```

**Subcommands:**

- [config](#config): Manage per-environment application configuration.
- [deploy](#deploy): Deploy APP_NAME to the target environment.
- [logs](#logs): Stream or display recent logs for APP_NAME.
- [rollback](#rollback): Roll back APP_NAME to its previous version.
- [status](#status): Check the deployment status of APP_NAME.

## config

...
~~~

Each entry links to the corresponding section anchor, so readers can jump straight to what they need. Hidden commands are excluded from the list unless you also pass `--show-hidden`.

---

## 9. Clean up the ASCII art

The `\b` block in the root command's help text renders as raw ASCII art in the Markdown output, which looks fine in a terminal but messy on a documentation page. Use `--remove-ascii-art` to strip it:

```console
$ click-docs deployer.py --program-name deployer --remove-ascii-art
```

The root section goes from this:

~~~markdown
# deployer

 ____             _
|  _ \  ___ _ __ | | ___  _   _  ___ _ __
...

A tool for deploying and managing web applications.
~~~

To this:

~~~markdown
# deployer

A tool for deploying and managing web applications.
~~~

The `\b` block and the blank line following it are removed. Everything after that blank line is kept.

---

## 10. Customize the header hierarchy

**Starting depth**

By default, the root command uses a level-1 heading (`#`). If you're embedding the output into a larger document that already has a level-1 title, use `--header-depth` to start deeper:

```console
$ click-docs deployer.py --program-name deployer --header-depth 2
```

The root uses `##`, its subcommands use `###`, and `config`'s sub-subcommands use `####`.

**Full command paths in headers**

By default, subcommand headings show only the command's own name — `## config`, `### get`. If you want headers to reflect the full invocation path (useful when embedding multiple CLIs in one page), use `--full-command-path`:

```console
$ click-docs deployer.py --program-name deployer --full-command-path
```

~~~markdown
## deployer config

...

### deployer config get

...

### deployer config list

...
~~~

---

## 11. Persist your settings in pyproject.toml

Typing the same flags on every run gets old quickly. click-docs reads its configuration from `[tool.click-docs]` in your `pyproject.toml`, so you can set your preferred defaults once and forget about them.

Add this to your `pyproject.toml`:

```toml title="pyproject.toml"
[tool.click-docs]
program-name = "deployer"
remove-ascii-art = true
list-subcommands = true
style = "table"
output = "docs/cli-reference.md"
```

Now a bare invocation applies all of those settings automatically:

```console
$ click-docs deployer.py
```

That single command generates `docs/cli-reference.md` with the table style, no ASCII art, and a subcommand TOC — every time.

Any flag you pass on the command line overrides the config file. So if you occasionally want a plain-style version without rewriting your config:

```console
$ click-docs deployer.py --style plain --output docs/cli-reference-plain.md
```

!!! tip

    click-docs searches for `pyproject.toml` starting from your current working directory and walking up to the filesystem root. You don't need to be in the same directory as `deployer.py` — as long as you're somewhere inside your project, click-docs will find the config.

---

## What you've learned

Here's everything covered in this tutorial:

| Goal | Flag |
| --- | --- |
| Limit recursion depth | `--depth N` |
| Exclude a branch | `--exclude cli.config` |
| Reveal hidden commands and options | `--show-hidden` |
| Use Markdown table for options | `--style table` |
| Add a subcommand TOC | `--list-subcommands` |
| Strip ASCII art | `--remove-ascii-art` |
| Start at a deeper heading level | `--header-depth 2` |
| Show full command paths in headers | `--full-command-path` |
| Persist defaults | `pyproject.toml [tool.click-docs]` |

You now have the full toolkit. Between `--depth`, `--exclude`, `--show-hidden`, `--style`, and `pyproject.toml` configuration, you can generate exactly the documentation your project needs — for any Click application, from a three-command script to a deeply nested CLI with hundreds of subcommands.
