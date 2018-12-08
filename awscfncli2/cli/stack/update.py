# -*- encoding: utf-8 -*-

import click
import botocore.exceptions

from . import stack
from ..utils import command_exception_handler
from ...cli import ClickContext
from ...runner import StackUpdateOptions, StackUpdateCommand
from ...config import CANNED_STACK_POLICIES


@stack.command()
@click.option('--no-wait', '-w', is_flag=True, default=False,
              help='Exit immediately after update is started.')
@click.option('--use-previous-template', is_flag=True, default=False,
              help='Reuse the existing template that is associated with the '
                   'stack that you are updating.')
@click.option('--ignore-no-update', '-i', is_flag=True, default=False,
              help='Ignore error when there are no updates to be performed.')
@click.option('--override-policy',
              type=click.Choice(CANNED_STACK_POLICIES.keys()),
              default=None,
              help='Temporary overriding stack policy during this update.'
                   'Valid canned policy are: \b\n'
                   'ALLOW_ALL: Allows all updates\n'
                   'DENY_DELETE: Allows modify and replace, denys delete\n'
                   'ALLOW_MODIFY: Allows modify, denys replace and delete\n')
@click.pass_context
@command_exception_handler
def update(ctx, no_wait, use_previous_template, ignore_no_update,
           override_policy):
    """Update an existing stack"""
    assert isinstance(ctx.obj, ClickContext)

    options = StackUpdateOptions(
        no_wait=no_wait,
        use_previous_template=use_previous_template,
        ignore_no_update=ignore_no_update,
        override_policy=override_policy
    )

    command = StackUpdateCommand(
        pretty_printer=ctx.obj.ppt,
        options=options
    )

    ctx.obj.runner.run(command)
