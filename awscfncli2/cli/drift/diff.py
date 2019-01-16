#  -*- encoding: utf-8 -*-

import click
import botocore.exceptions

from . import drift
from ..utils import command_exception_handler
from ...cli import ClickContext
from ...runner import DriftDiffOptions, DriftDiffCommand


@drift.command()

@click.pass_context
@command_exception_handler
def diff(ctx):
    """Show stack resource drifts."""
    assert isinstance(ctx.obj, ClickContext)

    options = DriftDiffOptions(
    )

    command = DriftDiffCommand(
        pretty_printer=ctx.obj.ppt,
        options=options
    )

    ctx.obj.runner.run(command)
