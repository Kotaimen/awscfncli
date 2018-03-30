# -*- encoding: utf-8 -*-

import click

from . import stack
from ..utils import boto3_exception_handler, \
    pretty_print_stack, custom_paginator, echo_pair, ContextObject, \
    STACK_STATUS_TO_COLOR
from ..utils import tail_stack_events
from ...config import CANNED_STACK_POLICIES


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

    stack_config = ctx.obj.stacks[0]

    session = ctx.obj.get_boto3_session(stack_config)
    region = stack_config['Metadata']['Region']

    cloudformation = session.resource(
        'cloudformation',
        region_name=region
    )

    stack = cloudformation.Stack(stack_config['StackName'])

    tail_stack_events(session, stack, latest_events=events, time_limit=timeout)
