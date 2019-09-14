#  -*- encoding: utf-8 -*-

import click

from awscfncli2.cli.context import Context
from awscfncli2.cli.utils.deco import command_exception_handler
from awscfncli2.runner.commands.drift_diff_command import DriftDiffOptions, \
    DriftDiffCommand


@click.command()
@click.pass_context
@command_exception_handler
def diff(ctx):
    """Show stack resource drifts."""
    assert isinstance(ctx.obj, Context)

    options = DriftDiffOptions(
    )

    command = DriftDiffCommand(
        pretty_printer=ctx.obj.ppt,
        options=options
    )

    ctx.obj.runner.run(command)
