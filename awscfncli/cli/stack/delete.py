#  -*- encoding: utf-8 -*-

import six
import click

from . import stack
from ..utils import ContextObject
from ..utils import boto3_exception_handler
from ..utils import pretty_print_stack, echo_pair
from ..utils import start_tail_stack_events_daemon


@stack.command()
@click.option('--no-wait', is_flag=True, default=False,
              help='Exit immediately after operation is started.')
@click.option('--quiet', is_flag=True, default=False,
              help='Suppress warning if more than one stack is being deleted.')
@click.pass_context
@boto3_exception_handler
def delete(ctx, no_wait, quiet):
    """Delete stacks"""
    assert isinstance(ctx.obj, ContextObject)

    selected_stacks = list(six.iteritems(ctx.obj.stacks))

    # prompt user if more than
    if len(selected_stacks) > 1:
        if not quiet:
            click.confirm('Do you want to delete more than one stacks?  '
                          'Be more specific using --stack option.', abort=True)

    # reverse creation order
    selected_stacks.reverse()

    for qualified_name, stack_config in selected_stacks:
        echo_pair(qualified_name, key_style=dict(bold=True), sep='')
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
