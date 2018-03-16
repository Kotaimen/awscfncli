#  -*- encoding: utf-8 -*-

import click
from . import stack
from ..utils import ContextObject
from ..utils import boto3_exception_handler
from ..utils import pretty_print_stack
from ..utils import start_tail_stack_events_daemon


@stack.command()
@click.argument('env_pattern', envvar='CFN_ENV_PATTERN')
@click.argument('stack_pattern', envvar='CFN_STACK_PATTERN')
@click.option('--no-wait', is_flag=True, default=False,
              help='Exit immediately after operation is started.')
@click.option('--on-failure',
              type=click.Choice(['DO_NOTHING', 'ROLLBACK', 'DELETE']),
              default=None,
              help='Determines what action will be taken if stack creation '
                   'fails. This must be one of: DO_NOTHING, ROLLBACK, or '
                   'DELETE. Note setting this option overwrites "OnFailure" '
                   'and "DisableRollback" in the stack configuration file.')
@boto3_exception_handler
@click.pass_context
def deploy(ctx, env_pattern, stack_pattern, no_wait, on_failure):
    """Deploy a new stack using specified stack configuration file"""
    assert isinstance(ctx.obj, ContextObject)

    stack_config \
        = ctx.obj.find_one_stack_config(env_pattern=env_pattern,
                                        stack_pattern=stack_pattern)

    session = ctx.obj.get_boto3_session(stack_config)
    region = stack_config['Metadata']['Region']

    # option handling
    if on_failure is not None:
        stack_config.pop('DisableRollback', None)
        stack_config['OnFailure'] = on_failure

    # connect to cloudformation
    cloudformation = session.resource(
        'cloudformation',
        region_name=region)

    # pop metadata form stack config
    metadata = stack_config.pop('Metadata')

    # create stack
    stack = cloudformation.create_stack(**stack_config)
    stack_id = stack.stack_id
    pretty_print_stack(stack)

    # exit immediately
    if no_wait:
        return

    # start event tailing
    start_tail_stack_events_daemon(session, stack, latest_events=0)

    # wait until update complete
    waiter = session.client('cloudformation', region_name=region). \
        get_waiter('stack_create_complete')
    waiter.wait(StackName=stack_id)

    click.secho('Stack deployment complete.', fg='green')
