#  -*- encoding: utf-8 -*-

import click

from . import stack
from ..utils import command_exception_handler
from ...cli import ClickContext
from ...runner import StackDeployOptions, StackDeployCommand

@stack.command()
@click.option('--no-wait', is_flag=True, default=False,
              help='Exit immediately after operation is started.')
@click.option('--on-failure',
              type=click.Choice(['DO_NOTHING', 'ROLLBACK', 'DELETE']),
              default=None,
              help='Determines what action will be taken if stack creation '
                   'fails. This must be one of: DO_NOTHING, ROLLBACK, or '
                   'DELETE. Note setting this option overwrites "OnFailure" '
                   'and "DisableRollback" in the stack configuration file.')
@click.option('--ignore-existing', '-r', is_flag=True, default=False,
              help='Don\'t report error if the stack already exists.')

@click.pass_context
@command_exception_handler
def deploy(ctx, no_wait, on_failure, ignore_existing):
    """Deploy a new stack"""
    assert isinstance(ctx.obj, ClickContext)

    options = StackDeployOptions(
        no_wait=no_wait,
        on_failure=on_failure,
        ignore_existing=ignore_existing
    )

    command = StackDeployCommand(
        pretty_printer=ctx.obj.ppt,
        options=options
    )

    ctx.obj.runner.run(command)
