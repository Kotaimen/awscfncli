import click

from awscfncli2.cli.context import Context
from awscfncli2.cli.utils.deco import command_exception_handler
from awscfncli2.runner.commands.stack_status_command import StackStatusOptions, \
    StackStatusCommand


# TODO: Deprecate this

@click.command()
@click.option('--stack-resources', '-r', is_flag=True, default=True,
              help='Display stack resources.')
@click.option('--stack-exports', '-e', is_flag=True, default=True,
              help='Display stack exports.')
@click.pass_context
@command_exception_handler
def describe(ctx, stack_resources, stack_exports):
    """Deprecated, use "status" command instead."""

    assert isinstance(ctx.obj, Context)

    ctx.obj.ppt.secho('Deprecated, use "status" command instead!', fg='red')

    options = StackStatusOptions(
        dry_run=False,
        stack_resources=stack_resources,
        stack_exports=stack_exports,
    )

    command = StackStatusCommand(
        pretty_printer=ctx.obj.ppt,
        options=options
    )

    ctx.obj.runner.run(command)
