# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '11/01/2017'

import click

from ...cli import stack
from ...config import load_stack_config
from ..utils import boto3_exception_handler, pretty_print_config, \
    pretty_print_stack, load_template_body, CANNED_STACK_POLICIES
from .events import tail_stack_events, start_tail_stack_events_daemon


@stack.command()
@click.argument('config_file', type=click.Path(exists=True))
@click.option('--no-wait', is_flag=True, default=False,
              help='Exit immediately after operation is started.')
@click.option('--on-failure',
              type=click.Choice(['DO_NOTHING', 'ROLLBACK', 'DELETE']),
              default=None,
              help='Determines what action will be taken if stack creation '
                   'fails. This must be one of: DO_NOTHING, ROLLBACK, or '
                   'DELETE. Note setting this option overwrites "OnFailure" '
                   'and "DisableRollback" in the stack configuration file.')
@click.option('--canned-policy',
              type=click.Choice(['ALLOW_MODIFY',
                                 'DENY_DELETE', 'DENY_ALL', ]),
              default=None,
              help='Attach a predefined Stack Policy as StackPolicyBody when '
                   'deploying the stack.  A Stack Policy controls whether '
                   'change to stack resources are allowed during stack update.  '
                   'Valid canned policy are: \b\n'
                   'DENY_DELETE: Allows modify and replace, denys delete\n'
                   'ALLOW_MODIFY: Allows modify, denys replace and delete\n'
                   'DENY_ALL: Denys all updates\n'
                   'Note setting this option overwrites "PolicyBody" and '
                   '"PolicyURL" in the stack configuration file.')
@click.pass_context
@boto3_exception_handler
def deploy(ctx, config_file, no_wait, on_failure, canned_policy):
    """Deploy a new stack using specified stack configuration file

    CONFIG_FILE         Stack configuration file.
    """

    session = ctx.obj['session']

    # load config
    stack_config = load_stack_config(config_file)
    click.echo('Deploying stack...')
    pretty_print_config(stack_config)

    load_template_body(session, stack_config)

    # option handling
    if on_failure is not None:
        stack_config.pop('DisableRollback', None)
        stack_config['OnFailure'] = on_failure

    if canned_policy is not None:
        stack_config.pop('StackPolicyURL', None)
        stack_config['StackPolicyBody'] = CANNED_STACK_POLICIES[canned_policy]

    # connect to cfn
    region = stack_config.pop('Region')

    # remove unused parameters
    stack_config.pop('Package', None)

    cfn = session.resource('cloudformation', region_name=region)

    # create stack
    stack = cfn.create_stack(**stack_config)
    stack_id = stack.stack_id
    pretty_print_stack(stack)

    # exit immediately
    if no_wait:
        return

    # start event tailing
    start_tail_stack_events_daemon(session, stack, latest_events=0)

    # wait until update complete
    waiter = session.client('cloudformation', region_name=region).get_waiter(
        'stack_create_complete')
    waiter.wait(StackName=stack_id)

    click.secho('Stack deployment complete.', fg='green')
