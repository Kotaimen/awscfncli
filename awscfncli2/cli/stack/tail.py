# -*- encoding: utf-8 -*-

import click

from . import stack
from ..utils import command_exception_handler, tail_stack_events
from ...cli import ClickContext


@stack.command()
@click.option('--timeout', '-t', type=click.IntRange(min=0, max=3600),
              default=300, help='wait time in seconds before exit')
@click.option('--events', '-n', type=click.IntRange(min=0, max=100),
              default=0,
              help='number of latest stack events, 0 means fetch all'
                   'stack events')
@click.pass_context
@command_exception_handler
def tail(ctx, timeout, events):
    """Wath stack events, not this command will only select first one
    if mutable stacks matches stack selector."""
    assert isinstance(ctx.obj, ClickContext)

    for stack_context in ctx.obj.runner.contexts:
        stack_context.make_boto3_parameters()

        ctx.obj.ppt.pprint_stack_name(
            stack_context.stack_key,
            stack_context.parameters['StackName'],
            'Stack events for '
        )

        session = stack_context.session
        cfn = session.resource('cloudformation')
        stack = cfn.Stack(stack_context.parameters['StackName'])

        tail_stack_events(session, stack, latest_events=events,
                          time_limit=timeout)
