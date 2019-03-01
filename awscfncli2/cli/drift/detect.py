#  -*- encoding: utf-8 -*-

import click
import botocore.exceptions

from . import drift
from ..utils import command_exception_handler
from ...cli import ClickContext
from ...runner import DriftDetectOptions, DriftDetectCommand


@drift.command()
@click.option('--no-wait', '-w', is_flag=True, default=False,
              help='Exit immediately after operation is started.')
@click.pass_context
@command_exception_handler
def detect(ctx, no_wait):
    """Detect stack drifts."""
    assert isinstance(ctx.obj, ClickContext)

    options = DriftDetectOptions(
        no_wait=no_wait,
    )

    command = DriftDetectCommand(
        pretty_printer=ctx.obj.ppt,
        options=options
    )

    ctx.obj.runner.run(command)
