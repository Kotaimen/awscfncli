# -*- encoding: utf-8 -*-

import click

from . import stack
from ..utils import boto3_exception_handler, \
    pretty_print_stack, custom_paginator, echo_pair, ContextObject, \
    STACK_STATUS_TO_COLOR
from ..utils import tail_stack_events
from ...config import CANNED_STACK_POLICIES


@stack.command()
@click.argument('stage_pattern', envvar='CFN_STAGE_PATTERN')
@click.argument('stack_pattern', envvar='CFN_STACK_PATTERN')
@click.option('--timeout', '-t', type=click.IntRange(min=0, max=3600),
              default=300, help='wait time in seconds before exit')
@click.option('--events', '-n', type=click.IntRange(min=0, max=100),
              default=0,
              help='number of latest stack events, 0 means fetch all'
                   'stack events')
@click.pass_context
@boto3_exception_handler
def tail(ctx, stage_pattern, stack_pattern,
         timeout, events):
    """Update stack with configuration"""
    assert isinstance(ctx.obj, ContextObject)

    stack_config \
        = ctx.obj.find_one_stack_config(stage_pattern=stage_pattern,
                                        stack_pattern=stack_pattern)

    session = ctx.obj.get_boto3_session(stack_config)
    region = stack_config['Metadata']['Region']

    cloudformation = session.resource(
        'cloudformation',
        region_name=region
    )

    stack = cloudformation.Stack(stack_config['StackName'])

    tail_stack_events(session, stack, latest_events=events, time_limit=timeout)
