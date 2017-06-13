# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '11/01/2017'

import click

from ..utils import boto3_exception_handler, pretty_print_config, \
    pretty_print_stack, load_template_body, CANNED_STACK_POLICIES
from ...cli import stack
from ...config import load_stack_config
from .events import start_tail_stack_events_daemon


@stack.command()
@click.argument('config_file', type=click.Path(exists=True))
@click.option('--no-wait', is_flag=True, default=False,
              help='Exit immediately after operation is started.')
@click.option('--use-previous-template', is_flag=True, default=False,
              help='Reuse the existing template that is associated with the '
                   'stack that you are updating.')
@click.option('--canned-policy',
              type=click.Choice(['ALLOW_ALL', 'ALLOW_MODIFY',
                                 'DENY_DELETE', 'DENY_ALL', ]),
              default=None,
              help='A predefined Stack Policy as StackPolicyBody when '
                   'updating the stack.  A Stack Policy controls whether '
                   'change to stack resources are allowed during stack update.  '
                   'Valid canned policy are: \b\n'
                   'ALLOW_ALL: Allows all updates\n'
                   'DENY_DELETE: Allows modify and replace, denys delete\n'
                   'ALLOW_MODIFY: Allows modify, denys replace and delete\n'
                   'DENY_ALL: Denys all updates\n'
                   'Note setting this option overwrites "PolicyBody" and '
                   '"PolicyURL" in the stack configuration file.')
@click.option('--override-policy',
              type=click.Choice(['ALLOW_ALL', 'ALLOW_MODIFY',
                                 'DENY_DELETE']),
              default=None,
              help='Temporary overriding stack policy during this update.'
                   'Valid canned policy are: \b\n'
                   'ALLOW_ALL: Allows all updates\n'
                   'DENY_DELETE: Allows modify and replace, denys delete\n'
                   'ALLOW_MODIFY: Allows modify, denys replace and delete\n')
@click.pass_context
@boto3_exception_handler
def update(ctx, config_file, no_wait, use_previous_template,
           canned_policy, override_policy):
    """Update the stack specified in the configuration file.

    CONFIG_FILE         Stack configuration file.
    """
    session = ctx.obj['session']

    # load config
    stack_config = load_stack_config(config_file)
    pretty_print_config(stack_config)
    load_template_body(session, stack_config)

    click.echo('Updating stack...')

    # connect co cfn
    region = stack_config.pop('Region')

    # remove unused parameters
    stack_config.pop('Package', None)

    cfn = session.resource('cloudformation', region_name=region)
    stack = cfn.Stack(stack_config['StackName'])

    # remove unused parameters
    stack_config.pop('DisableRollback', None)
    stack_config.pop('OnFailure', None)

    # update parameters
    if use_previous_template:
        stack_config.pop('TemplateBody', None)
        stack_config.pop('TemplateURL', None)
        stack_config['UsePreviousTemplate'] = use_previous_template

    if canned_policy is not None:
        stack_config.pop('StackPolicyURL', None)
        stack_config['StackPolicyBody'] = CANNED_STACK_POLICIES[canned_policy]

    if override_policy is not None:
        click.echo('Overriding stack policy during update...')
        stack_config['StackPolicyDuringUpdateBody'] = \
            CANNED_STACK_POLICIES[override_policy]

    stack_id = stack.stack_id
    pretty_print_stack(stack)

    # update stack
    stack.update(**stack_config)

    # exit immediately
    if no_wait:
        return

    # start event tailing
    start_tail_stack_events_daemon(session, stack, latest_events=2)

    # wait until update complete
    waiter = session.client('cloudformation', region_name=region).get_waiter(
        'stack_update_complete')
    waiter.wait(StackName=stack_id)

    click.secho('Stack update complete.', fg='green')
