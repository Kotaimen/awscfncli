# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '11/01/2017'

import click

from ..utils import boto3_exception_handler
from ...cli import stack
from ...config import load_stack_config
from .events import tail_stack_events


@stack.command()
@click.argument('config_file', type=click.Path(exists=True))
@click.option('--timeout', '-t', type=click.IntRange(min=0, max=3600),
              default=300, help='wait time in seconds before exit')
@click.option('--events', '-n', type=click.IntRange(min=0, max=100),
              default=0,
              help='number of latest stack events, 0 means fetch all'
                   'stack events')
@click.pass_context
@boto3_exception_handler
def tail(ctx, config_file, timeout, events):
    """Print stack events and waiting for update (stop using CTRL+C)

    CONFIG_FILE         Stack configuration file.
    """
    session = ctx.obj['session']

    stack_config = load_stack_config(config_file)

    cfn = session.resource('cloudformation', region_name=stack_config['Region'])
    stack = cfn.Stack(stack_config['StackName'])

    tail_stack_events(session, stack, latest_events=events, time_limit=timeout)
