#  -*- encoding: utf-8 -*-

import click
from . import stack
from ..utils import command_exception_handler
from ...cli import ClickContext
from ...runner import StackDeployOptions, StackDeployCommand


@stack.command()
@click.option('--no-wait', '-w', is_flag=True, default=False,
              help='Exit immediately after deploy is started.')
@click.option('--on-failure',
              type=click.Choice(['DO_NOTHING', 'ROLLBACK', 'DELETE']),
              default=None,
              help='Determines what action will be taken if stack creation '
                   'fails. This must be one of: DO_NOTHING, ROLLBACK, or '
                   'DELETE. Setting this option overwrites "OnFailure" '
                   'in the stack configuration file.')
@click.option('--disable-rollback',
              is_flag=True, default=False,
              help='Disable rollback if stack creation failed. You can specify '
                   'either DisableRollback or OnFailure, but not both. '
                   'Setting this option overwrites "DisableRollback" '
                   'in the stack configuration file.')
@click.option('--timeout-in-minutes',
              type=click.IntRange(min=0, max=180),
              help='The amount of time in minutes that can pass before the stack '
                   'status becomes CREATE_FAILED; if DisableRollback is not set or '
                   'is set to false , the stack will be rolled back.  ')
@click.option('--ignore-existing', '-i', is_flag=True, default=False,
              help='Don\'t exit with error if the stack already exists.')
@click.pass_context
@command_exception_handler
def deploy(ctx, no_wait, on_failure,
           disable_rollback,
           timeout_in_minutes,
           ignore_existing, ):
    """Deploy a new stack"""
    assert isinstance(ctx.obj, ClickContext)

    try:    
        auto_deploy = ctx.obj.global_settings.getboolean('behaviours', 'auto_deploy', fallback=False)
    except Exception as ex:
        ctx.obj.ppt.secho("Error processing Global Config file:\n " + str(ex), fg='red')
        return

    options = StackDeployOptions(
        no_wait=no_wait,
        on_failure=on_failure,
        disable_rollback=disable_rollback,
        timeout_in_minutes=timeout_in_minutes,
        ignore_existing=ignore_existing,
        auto_deploy=auto_deploy
    )

    command = StackDeployCommand(
        pretty_printer=ctx.obj.ppt,
        options=options
    )

    ctx.obj.runner.run(command)
