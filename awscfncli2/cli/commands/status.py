#  -*- encoding: utf-8 -*-

import click
import botocore.exceptions

from ..main import cfn_cli
from ..utils import command_exception_handler
from ...cli import ClickContext
from ...runner import StackStatusOptions, StackStatusCommand


@cfn_cli.command()
@click.option('--dry-run', '-d', is_flag=True, default=False,
              help='Don\'t retrieve stack deployment status (faster).')
@click.option('--stack-resources', '-r', is_flag=True, default=False,
              help='Display stack resources.')
@click.option('--stack-exports', '-e', is_flag=True, default=False,
              help='Display stack exports.')
@click.pass_context
@command_exception_handler
def status(ctx, dry_run, stack_resources, stack_exports):
    """Alias for `stack describe`."""
    assert isinstance(ctx.obj, ClickContext)

    # shortcut if we only print stack key (and names)
    if dry_run:
        for context in ctx.obj.runner.contexts:
            ctx.obj.ppt.secho(context.stack_key, bold=True)
        return

    options = StackStatusOptions(
        dry_run=dry_run,
        stack_resources=stack_resources,
        stack_exports=stack_exports,
    )

    command = StackStatusCommand(
        pretty_printer=ctx.obj.ppt,
        options=options
    )

    ctx.obj.runner.run(command)
