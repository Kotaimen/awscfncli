#  -*- encoding: utf-8 -*-

import click

from . import stack
from ..utils import ContextObject
from ..utils import boto3_exception_handler
from ..utils import pretty_print_stack, echo_pair
from ..utils import start_tail_stack_events_daemon


@stack.command()
@click.option('--no-wait', is_flag=True, default=False,
              help='Exit immediately after operation is started.')
@click.pass_context
@boto3_exception_handler
def delete(ctx, no_wait):
    """Delete stack."""
    assert isinstance(ctx.obj, ContextObject)

    for stack_config in ctx.obj.stacks:
        echo_pair(stack_config['Metadata']['QualifiedName'],
                  key_style=dict(bold=True), sep='')
        delete_one(ctx, stack_config, no_wait)


def delete_one(ctx, stack_config, no_wait):
    session = ctx.obj.get_boto3_session(stack_config)
    region = stack_config['Metadata']['Region']

    # connect to cloudformation
    cloudformation = session.resource(
        'cloudformation',
        region_name=region)

    # connect to stack
    stack = cloudformation.Stack(stack_config['StackName'])
    stack_id = stack.stack_id

    pretty_print_stack(stack)

    # delete the stack
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
