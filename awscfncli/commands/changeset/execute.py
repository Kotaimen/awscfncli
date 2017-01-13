# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '13/01/2017'

import boto3
import click

from ..utils import boto3_exception_handler, pretty_print_config
from ..stack.events import start_tail_stack_events_daemon
from ...cli import changeset
from ...config import load_stack_config


@changeset.command()
@click.argument('config_file', type=click.Path(exists=True))
@click.argument('changeset_name')
@click.pass_context
@boto3_exception_handler
def execute(ctx, config_file, changeset_name):
    """Updates a stack using the input information that was provided when
    the specified change set was created.

    \b
    CONFIG_FILE         Stack configuration file.
    CHANGESET_NAME      The name of the change set.
    """
    # load config
    stack_config = load_stack_config(config_file)
    pretty_print_config(stack_config)

    # connect to cfn
    region = stack_config.pop('Region')

    # execute change set
    client = boto3.client('cloudformation', region_name=region)
    cfn = boto3.resource('cloudformation', region_name=region)
    stack = cfn.Stack(stack_config['StackName'])

    # HACK:
    if stack.stack_status == 'REVIEW_IN_PROGRESS':
        waiter_model = 'stack_create_complete'
    else:
        waiter_model = 'stack_update_complete'

    client.execute_change_set(
        ChangeSetName=changeset_name,
        StackName=stack_config['StackName'],
    )

    # start event tailing
    start_tail_stack_events_daemon(stack, latest_events=5)

    # wait until update complete
    waiter = client.get_waiter(waiter_model)
    waiter.wait(StackName=stack.stack_id)

    click.echo(click.style('ChangSet execution complete.',
                           fg='green'))
