import click

from . import stack

from ..utils import command_exception_handler
from ...cli import ClickContext
from ...runner import StackStatusOptions, StackStatusCommand


@stack.command()
@click.option('--stack-resources', '-r', is_flag=True, default=True,
              help='Display stack resources.')
@click.option('--stack-exports', '-e', is_flag=True, default=True,
              help='Display stack exports.')
@click.pass_context
@command_exception_handler
def describe(ctx, stack_resources, stack_exports):
    """List deployment status, resources and of stacks, identical with stack
    status command but defaults to print all information"""
    assert isinstance(ctx.obj, ClickContext)

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
