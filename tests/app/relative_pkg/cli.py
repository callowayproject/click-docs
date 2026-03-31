"""Fixture CLI that uses a relative import, to test loader's relative-import support."""

import click

from .helpers import GREETING


@click.command()
def cli() -> None:
    """Command loaded from a package that uses relative imports."""
    click.echo(GREETING)
