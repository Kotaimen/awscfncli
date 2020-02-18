import click

from awscfncli2.cli.utils.deco import command_exception_handler
from awscfncli2.runner.commands.stack_status_command import StackStatusOptions, StackStatusCommand


@click.command('status')
@click.option('--dry-run', '-d', is_flag=True, default=False,
              help='Don\'t retrieve stack deployment status (faster).')
@click.option('--stack-resources', '-r', is_flag=True, default=False,
              help='Display stack resources.')
@click.option('--stack-exports', '-e', is_flag=True, default=False,
              help='Display stack exports.')
@click.pass_context
@command_exception_handler
def cli(ctx, dry_run, stack_resources, stack_exports):
    """Print stack status and resources.

    Also includes parameters, resources, outputs & exports."""

    # shortcut if we only print stack key (and names)
    if dry_run:
        for context in ctx.obj.runner.contexts:
            ctx.obj.ppt.secho(context.stack_key, bold=True)
        return

    options = StackStatusOptions(
        dry_run=dry_run,
        stack_resources=stack_resources,
        stack_exports=stack_exports,
    )

    command = StackStatusCommand(
        pretty_printer=ctx.obj.ppt,
        options=options
    )

    ctx.obj.runner.run(command)
