# -*- encoding: utf-8 -*-

import click
import botocore.exceptions

from . import stack
from ..utils import boto3_exception_handler, pretty_print_config, \
    pretty_print_stack, ContextObject
from ..utils import start_tail_stack_events_daemon
from ..utils import run_packaging
from ...config import CANNED_STACK_POLICIES


@stack.command()
@click.option('--no-wait', is_flag=True, default=False,
              help='Exit immediately after operation is started.')
@click.option('--use-previous-template', is_flag=True, default=False,
              help='Reuse the existing template that is associated with the '
                   'stack that you are updating.')
@click.option('--ignore-no-update', is_flag=True, default=False,
              help='Ignore error when there are no updates to be performed.')
@click.option('--override-policy',
              type=click.Choice(CANNED_STACK_POLICIES.keys()),
              default=None,
              help='Temporary overriding stack policy during this update.'
                   'Valid canned policy are: \b\n'
                   'ALLOW_ALL: Allows all updates\n'
                   'DENY_DELETE: Allows modify and replace, denys delete\n'
                   'ALLOW_MODIFY: Allows modify, denys replace and delete\n')
@click.pass_context
@boto3_exception_handler
def update(ctx, no_wait, use_previous_template, ignore_no_update, override_policy):
    """Update stack with configuration"""
    assert isinstance(ctx.obj, ContextObject)

    for qualified_name, stack_config in ctx.obj.stacks.items():
        session = ctx.obj.get_boto3_session(stack_config)
        pretty_print_config(qualified_name, stack_config, session,
                            ctx.obj.verbosity)
        update_one(ctx, session, stack_config, no_wait, use_previous_template,
                   ignore_no_update, override_policy)


def update_one(ctx, session, stack_config, no_wait, use_previous_template,
               ignore_no_update, override_policy):
    # package the template
    if use_previous_template:
        stack_config.pop('TemplateBody', None)
        stack_config.pop('TemplateURL', None)
        stack_config['UsePreviousTemplate'] = use_previous_template
    else:
        run_packaging(stack_config, session, ctx.obj.verbosity)

    # pop metadata form stack config
    stack_config.pop('Metadata')

    # stack = cloudformation.Stack(stack_config['StackName'])
    click.echo('Updating stack...')

    cfn = session.resource('cloudformation')
    stack = cfn.Stack(stack_config['StackName'])

    # remove unused parameters
    stack_config.pop('DisableRollback', None)
    stack_config.pop('OnFailure', None)
    termination_protection = stack_config.pop(
        'EnableTerminationProtection', None)

    if override_policy is not None:
        click.secho('Overriding stack policy during update...', fg='red')
        stack_config['StackPolicyDuringUpdateBody'] = \
            CANNED_STACK_POLICIES[override_policy]

    stack_id = stack.stack_id
    pretty_print_stack(stack)

    # termination protection should be updated
    # no matter stack's update succeeded or not
    if termination_protection is not None:
        client = session.client('cloudformation')
        click.secho(
            'Setting Termination Protection to "%s"' %
            termination_protection, fg='red')
        client.update_termination_protection(
            EnableTerminationProtection=termination_protection,
            StackName=stack_config['StackName']
        )

    # update stack
    if ctx.obj.verbosity > 0:
        click.echo(stack_config)

    try:
        stack.update(**stack_config)
    except botocore.exceptions.ClientError as e:
        if ignore_no_update:
            error = e.response.get('Error', {})
            error_message = error.get('Message', 'Unknown')
            if error_message.endswith('No updates are to be performed.'):
                click.secho('Warning: No updates are to be performed', fg='red')
                return
        raise

    # exit immediately
    if no_wait:
        return

    # start event tailing
    start_tail_stack_events_daemon(session, stack)

    # wait until update complete
    waiter = session.client('cloudformation').get_waiter('stack_update_complete')
    waiter.wait(StackName=stack_id)

    click.secho('Stack update complete.', fg='green')
