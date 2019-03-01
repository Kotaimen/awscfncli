#  -*- encoding: utf-8 -*-

import click
import botocore.exceptions

from . import stack
from ..utils import command_exception_handler
from ...cli import ClickContext


@stack.command()
@click.option('--no-wait', '-w', is_flag=True, default=False,
              help='Exit immediately after operation is started.')
@click.pass_context
@command_exception_handler
def cancel(ctx, no_wait):
    """Cancel current stack update"""
    assert isinstance(ctx.obj, ClickContext)

    for stack_context in ctx.obj.runner.contexts:
        stack_context.make_boto3_parameters()

        ctx.obj.ppt.pprint_stack_name(
            stack_context.stack_key,
            stack_context.parameters['StackName'],
            'Canceling update '
        )

        session = stack_context.session
        client = session.client('cloudformation')
        try:
            client.cancel_update_stack(StackName=stack_context.parameters['StackName'])
        except botocore.exceptions.ClientError as ex:
            error = ex.response.get('Error', {})
            error_message = error.get('Message', 'Unknown')
            if error_message.endswith('CancelUpdateStack cannot be called from current stack status'):
                click.secho(error_message)
            else:
                raise