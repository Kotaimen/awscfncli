# -*- encoding: utf-8 -*-
import click

from awscfncli2.cli.context import Context
from awscfncli2.cli.utils.deco import command_exception_handler
from awscfncli2.runner.commands.stack_sync_command import StackSyncOptions, \
    StackSyncCommand


@click.command()
@click.option('--no-wait', '-w', is_flag=True, default=False,
              help='Exit immediately after ChangeSet is created.')
@click.option('--confirm', is_flag=True, default=False,
              help='Review changes before execute the ChangeSet')
@click.option('--use-previous-template', is_flag=True, default=False,
              help='Reuse the existing template that is associated with the '
                   'stack that you are updating.')
@click.pass_context
@command_exception_handler
def sync(ctx, no_wait, confirm, use_previous_template):
    """Apply changes using ChangeSets

    Combines "aws cloudformation package" and "aws cloudformation deploy" command
    into one.  If stack is not created yet, a CREATE type ChangeSet is created,
    otherwise UPDATE ChangeSet is created.
    """
    assert isinstance(ctx.obj, Context)

    options = StackSyncOptions(
        no_wait=no_wait,
        confirm=confirm,
        use_previous_template=use_previous_template,
    )

    command = StackSyncCommand(
        pretty_printer=ctx.obj.ppt,
        options=options
    )

    ctx.obj.runner.run(command)
