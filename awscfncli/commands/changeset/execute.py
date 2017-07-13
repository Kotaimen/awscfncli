# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '13/01/2017'

import click

from ..utils import boto3_exception_handler, pretty_print_config, \
    load_template_body
from ..stack.events import start_tail_stack_events_daemon
from ...cli import changeset
from ...config import load_stack_config


@changeset.command()
@click.argument('config_file', type=click.Path(exists=True))
@click.argument('changeset_name')
@click.option('--no-wait', is_flag=True, default=False,
              help='Exit immediately after operation is started.')
@click.pass_context
@boto3_exception_handler
def execute(ctx, config_file, changeset_name, no_wait):
    """Updates stack using the change set.

    Updates a stack using the input information that was provided when the
    specified change set was created. After the call successfully completes,
    When you execute a change set, AWS CloudFormation deletes all other
    change sets associated with the stack because they aren't valid for
    the updated stack.

    If a stack policy is associated with the stack, AWS CloudFormation
    enforces the policy during the update. You can't specify a temporary
    stack policy that overrides the current policy.

    \b
    CONFIG_FILE         Stack configuration file.
    CHANGESET_NAME      The name of the change set.
    """
    session = ctx.obj['session']

    # load config
    stack_config = load_stack_config(config_file)
    pretty_print_config(stack_config)
    load_template_body(session, stack_config)

    # connect to cfn
    region = stack_config.pop('Region')

    # remove unused parameters
    stack_config.pop('Package', None)

    # execute change set
    client = session.client('cloudformation', region_name=region)
    cfn = session.resource('cloudformation', region_name=region)
    stack = cfn.Stack(stack_config['StackName'])

    if stack.stack_status == 'REVIEW_IN_PROGRESS':
        # HACK: stack created with a "create" type changeset (not deployed yet)
        waiter_model = 'stack_create_complete'
    else:
        waiter_model = 'stack_update_complete'

    client.execute_change_set(
        ChangeSetName=changeset_name,
        StackName=stack_config['StackName'],
    )

    # exit immediately
    if no_wait:
        return

    # start event tailing
    start_tail_stack_events_daemon(session, stack, latest_events=5)

    # wait until update complete
    waiter = client.get_waiter(waiter_model)
    waiter.wait(StackName=stack.stack_id)

    click.secho('ChangSet execution complete.',fg='green')
