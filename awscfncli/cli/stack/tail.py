# -*- encoding: utf-8 -*-

import click

from . import stack
from ..utils import boto3_exception_handler, ContextObject
from ..utils import tail_stack_events


@stack.command()
@click.option('--timeout', '-t', type=click.IntRange(min=0, max=3600),
              default=300, help='wait time in seconds before exit')
@click.option('--events', '-n', type=click.IntRange(min=0, max=100),
              default=0,
              help='number of latest stack events, 0 means fetch all'
                   'stack events')
@click.pass_context
@boto3_exception_handler
def tail(ctx, timeout, events):
    """Update stack with configuration"""
    assert isinstance(ctx.obj, ContextObject)

    qualified_name, stack_config = list(ctx.obj.stacks.items())[0]

    session = ctx.obj.get_boto3_session(stack_config)

    cloudformation = session.resource('cloudformation')

    stack = cloudformation.Stack(stack_config['StackName'])

    tail_stack_events(session, stack, latest_events=events, time_limit=timeout)
