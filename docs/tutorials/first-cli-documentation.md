---
title: Your First CLI Documentation
summary: Install click-docs and generate your first Markdown reference page from a Click application.
date: 2026-03-30T00:00:00+00:00
---

# Your First CLI Documentation

In this tutorial you'll install click-docs, write a small Click application, and generate a complete Markdown reference page from it — all in under ten minutes.

**What you'll build:** A fictional deployment tool called `deployer` with three subcommands, documented in a `docs/cli-reference.md` file that's ready to publish.

!!! note "Prerequisites"

    - Python 3.9 or later
    - Familiarity with Click — you should recognize a `@click.group()` and a `@click.command()`. If you haven't used Click before, their [quickstart guide](https://click.palletsprojects.com/en/stable/quickstart/) takes about ten minutes.

---

## 1. Install click-docs

Install with pip:

```console
$ pip install click-docs
```

Or, if your project uses `uv`:

```console
$ uv add click-docs
```

Confirm it's working:

```console
$ click-docs --help
```

You should see a usage line and a list of options. If you do, you're ready.

---

## 2. Create the CLI

Create a file called `deployer.py` in your project directory. This is the application we'll be documenting:

```python title="deployer.py"
import click


@click.group()
def cli():
    """A simple tool for deploying web applications."""


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
def deploy(app_name, env, version, dry_run):
    """Deploy APP_NAME to the target environment."""
    click.echo(f"Deploying {app_name} ({version}) to {env}...")


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
```

Nothing unusual here — a root `cli` group with three subcommands. This is a typical Click application.

---

## 3. Generate docs for the first time

From the directory containing `deployer.py`, run:

```console
$ click-docs deployer.py
```

click-docs loads your file, finds the `cli` object, introspects it, and prints Markdown to stdout:

~~~markdown
# cli

A simple tool for deploying web applications.

**Usage:**

```text
cli [OPTIONS] COMMAND [ARGS]...
```

**Options:**

```text
  --help  Show this message and exit.
```

## deploy

Deploy APP_NAME to the target environment.

**Usage:**

```text
cli deploy [OPTIONS] APP_NAME
```

**Options:**

```text
  -e, --env [staging|production]  Target deployment environment.  [default:
                                  staging]
  -v, --version TEXT              Application version tag to deploy.
                                  [default: latest]
  --dry-run                       Preview the deployment without executing it.
  --help                          Show this message and exit.
```

## rollback

Roll back APP_NAME to its previous version.

**Usage:**

```text
cli rollback [OPTIONS] APP_NAME
```

**Options:**

```text
  -e, --env [staging|production]  Environment to roll back.  [required]
  --help                          Show this message and exit.
```

## status

Check the deployment status of APP_NAME.

**Usage:**

```text
cli status [OPTIONS] APP_NAME
```

**Options:**

```text
  -e, --env [staging|production]  Environment to check status for.  [default:
                                  staging]
  --help                          Show this message and exit.
```
~~~

A few things to notice:

- Subcommands are listed in **alphabetical order** — `deploy`, `rollback`, `status` — regardless of the order they appear in the source file.
- The positional argument `APP_NAME` appears in the usage line but not in the options block. That matches Click's own `--help` output.
- click-docs never runs your application. It introspects the Click objects directly, so there are no side effects — no database connections, no network calls, nothing.

The output looks great, but notice the title says `cli`, not `deployer`. That's the Python variable name, not the name your users actually type. Let's fix that.

---

## 4. Set a friendlier program name

Pass `--program-name` to override the display name throughout the output:

```console
$ click-docs deployer.py --program-name deployer
```

The title and every usage line now use the real name:

~~~markdown
# deployer

A simple tool for deploying web applications.

**Usage:**

```text
deployer [OPTIONS] COMMAND [ARGS]...
```

...

**Usage:**

```text
deployer deploy [OPTIONS] APP_NAME
```
~~~

Much better. This is the name your users will recognise.

!!! tip

    If your CLI is installed as a script (via `[project.scripts]` in `pyproject.toml`), use that script name here. It's the name users type at the terminal and it's the name that should appear in the docs.

---

## 5. Write output to a file

Printing to stdout is handy for a quick look, but you'll want a file for your documentation site. Use `--output`:

```console
$ mkdir -p docs
$ click-docs deployer.py --program-name deployer --output docs/cli-reference.md
```

click-docs creates (or overwrites) `docs/cli-reference.md` with the full Markdown. Open it and you'll find the complete documentation for all three commands.

!!! tip

    Add this command to your `Makefile`, `tox.ini`, or CI pipeline so documentation is always regenerated from source. Because click-docs reads your Click objects directly, the docs can never drift out of sync as long as you re-run the command after updating your CLI.

---

## What you've learned

You've installed click-docs, pointed it at a Python file, and generated a complete Markdown reference page. Here's a quick recap:

| Goal | Flag |
| --- | --- |
| Generate to stdout | `click-docs deployer.py` |
| Override the program name | `--program-name deployer` |
| Write to a file | `--output docs/cli-reference.md` |

Your `deployer` has three commands and they're all documented. But real CLIs tend to be more interesting: nested subgroups, hidden admin commands, options with complex types, ASCII art banners. [Tutorial 2: Documenting a Real-World CLI](real-world-cli.md) walks through all of that.
