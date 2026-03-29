"""Fixture Click application for testing click-docs."""

import click

NOT_A_COMMAND = "not-a-command"


@click.command()
@click.option("--count", default=1, help="Number of greetings.")
@click.option("--name", required=True, help="The person to greet.")
def hello(count, name):
    """Simple program that greets NAME for a total of COUNT times."""


@click.group()
def cli():
    """Main entrypoint for this test app."""


cli.add_command(hello)


class NestedCommands:
    """Namespace for nested command access."""

    root = cli


@click.command()
@click.option("--fmt", type=click.Choice(["json", "yaml", "toml"]), help="Output format.")
@click.option("--level", type=click.IntRange(0, 10), help="Log level.")
@click.option("--ratio", type=click.FloatRange(0.0, 1.0), help="Ratio value.")
@click.option("--date", type=click.DateTime(["%Y-%m-%d", "%d/%m/%Y"]), help="A date.")
@click.option("--infile", type=click.File("r"), help="Input file.")
@click.option("--msg", help="Message.\f\nHidden text.")
def special_types(fmt, level, ratio, date, infile, msg):
    """Command with various special types."""
