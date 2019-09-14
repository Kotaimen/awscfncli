#  -*- encoding: utf-8 -*-

import click

from awscfncli2.cli.context import Context
from awscfncli2.cli.utils.deco import command_exception_handler
from awscfncli2.runner.commands.drift_detect_command import DriftDetectOptions, \
    DriftDetectCommand


@click.command()
@click.option('--no-wait', '-w', is_flag=True, default=False,
              help='Exit immediately after operation is started.')
@click.pass_context
@command_exception_handler
def detect(ctx, no_wait):
    """Detect stack drifts."""
    assert isinstance(ctx.obj, Context)

    options = DriftDetectOptions(
        no_wait=no_wait,
    )

    command = DriftDetectCommand(
        pretty_printer=ctx.obj.ppt,
        options=options
    )

    ctx.obj.runner.run(command)
