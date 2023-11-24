import click

from .cancel.cancel import cancel
from .delete.delete import delete
from .deploy.deploy import deploy
from .describe.describe import describe
from .sync.sync import sync
from .tail.tail import tail
from .update.update import update


@click.group()
@click.pass_context
def cli(ctx):
    """Stack operation sub-commands."""
    pass


cli.add_command(deploy)
cli.add_command(update)
cli.add_command(sync)
cli.add_command(tail)
cli.add_command(describe)
cli.add_command(cancel)
cli.add_command(delete)
