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
