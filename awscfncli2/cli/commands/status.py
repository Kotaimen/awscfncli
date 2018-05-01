#  -*- encoding: utf-8 -*-

import click
import botocore.exceptions

from ..main import cfn_cli
from ..utils import boto3_exception_handler, ContextObject
from ..utils import echo_pair, pretty_print_config, STACK_STATUS_TO_COLOR


@cfn_cli.command()
@click.option('-d', '--dry-run', is_flag=True, default=False,
              help='Don\'t retrieve stack deployment status (faster).')
@click.pass_context
@boto3_exception_handler
def status(ctx, dry_run):
    """List deployment status of selected stacks"""
    assert isinstance(ctx.obj, ContextObject)

    for qualified_name, stack_config in ctx.obj.stacks.items():
        session = ctx.obj.get_boto3_session(stack_config)

        pretty_print_config(qualified_name, stack_config, session, ctx.obj.verbosity,
                            retrieve_identity=True)

        if dry_run:
            continue

        cloudformation = session.resource('cloudformation')
        stack = cloudformation.Stack(stack_config['StackName'])

        try:
            stack_status = stack.stack_status
        except botocore.exceptions.ClientError as e:
            # only suppress "stack does not exist" error
            error = e.response.get('Error', {})
            error_message = error.get('Message', 'Unknown')
            if error_message.endswith('does not exist'):
                stack_status = 'STACK_NOT_FOUND'
            else:
                raise

        echo_pair('Status', stack_status,
                  value_style=STACK_STATUS_TO_COLOR[stack_status])
