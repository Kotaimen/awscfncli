#  -*- encoding: utf-8 -*-

import click

from . import stack
from ..utils import ContextObject, boto3_exception_handler, \
    run_packaging, pretty_print_config, pretty_print_stack, \
    start_tail_stack_events_daemon


@stack.command()
@click.option('--no-wait', is_flag=True, default=False,
              help='Exit immediately after operation is started.')
@click.option('--on-failure',
              type=click.Choice(['DO_NOTHING', 'ROLLBACK', 'DELETE']),
              default=None,
              help='Determines what action will be taken if stack creation '
                   'fails. This must be one of: DO_NOTHING, ROLLBACK, or '
                   'DELETE. Note setting this option overwrites "OnFailure" '
                   'and "DisableRollback" in the stack configuration file.')
@click.pass_context
@boto3_exception_handler
def deploy(ctx, no_wait, on_failure):
    """Deploy a new stack"""
    assert isinstance(ctx.obj, ContextObject)

    for qualified_name, stack_config in ctx.obj.stacks.items():
        session = ctx.obj.get_boto3_session(stack_config)
        pretty_print_config(qualified_name, stack_config, session,
                            ctx.obj.verbosity)
        deploy_one(ctx, session, stack_config, no_wait, on_failure)


def deploy_one(ctx, session, stack_config, no_wait, on_failure):
    # package the template
    run_packaging(stack_config, session, ctx.obj.verbosity)

    # option handling
    if on_failure is not None:
        stack_config.pop('DisableRollback', None)
        stack_config['OnFailure'] = on_failure

    # connect to cloudformation
    cloudformation = session.resource('cloudformation')

    # pop metadata form stack config
    stack_config.pop('Metadata')

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
    waiter = session.client('cloudformation').get_waiter(
        'stack_create_complete')
    waiter.wait(StackName=stack_id)

    click.secho('Stack deployment complete.', fg='green')
