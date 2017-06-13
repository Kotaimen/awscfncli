# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '11/01/2017'

import click

from ...cli import stack
from ...config import load_stack_config
from ..utils import boto3_exception_handler, pretty_print_config, \
    pretty_print_stack, load_template_body

from .events import start_tail_stack_events_daemon


@stack.command()
@click.argument('config_file', type=click.Path(exists=True))
@click.option('--no-wait', is_flag=True, default=False,
              help='Exit immediately after operation is started.')
@click.pass_context
@boto3_exception_handler
def delete(ctx, config_file, no_wait):
    """Delete the stack specified in the configuration file

    CONFIG_FILE         Stack configuration file.
    """
    session = ctx.obj['session']

    # load config
    stack_config = load_stack_config(config_file)
    pretty_print_config(stack_config)
    load_template_body(session, stack_config)
    click.echo('Deleting stack...')

    # connect co cfn
    region = stack_config.pop('Region')
    cfn = session.resource('cloudformation', region_name=region)
    stack = cfn.Stack(stack_config['StackName'])
    stack_id = stack.stack_id

    pretty_print_stack(stack)

    # delte the stack
    stack.delete()

    # exit immediately
    if no_wait:
        return

    # start event tailing
    start_tail_stack_events_daemon(session, stack, latest_events=2)

    # wait until delete complete
    waiter = session.client('cloudformation', region_name=region).get_waiter(
        'stack_delete_complete')
    waiter.wait(StackName=stack_id)

    click.secho('Stack delete complete.', fg='green')
