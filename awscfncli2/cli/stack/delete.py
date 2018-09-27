#  -*- encoding: utf-8 -*-

import click

from . import stack
from ..utils import command_exception_handler
from ...cli import ClickContext
from ...runner import StackDeleteOptions, StackDeleteCommand


@stack.command()
@click.option('--quiet', '-q', is_flag=True, default=False,
              help='Suppress warning if more than one stack is being deleted.')
@click.option('--no-wait', '-w', is_flag=True, default=False,
              help='Exit immediately after delete is started.')
@click.option('--ignore-missing', '-i', is_flag=True, default=False,
              help='Don\'t exit with error if the stack is missing.')
@click.pass_context
@command_exception_handler
def delete(ctx, quiet, no_wait, ignore_missing):
    """Delete stacks"""
    assert isinstance(ctx.obj, ClickContext)

    # prompt user if more than one stack is being deleted
    if len(ctx.obj.runner.contexts) > 1:
        if not quiet:
            click.confirm('Do you want to delete more than one stacks?  '
                          'Be more specific using --stack option.', abort=True)

    options = StackDeleteOptions(
        no_wait=no_wait,
        ignore_missing=ignore_missing
    )

    command = StackDeleteCommand(
        pretty_printer=ctx.obj.ppt,
        options=options
    )

    ctx.obj.runner.run(command, rev=True)

