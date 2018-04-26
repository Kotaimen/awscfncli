#  -*- encoding: utf-8 -*-

import click
import botocore.exceptions
import yaml

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
            stack.stack_status
        except botocore.exceptions.ClientError as e:
            echo_pair('Status', 'STACK_NOT_FOUND',
                      value_style=dict(fg='red', bold=True),
                      indent=2)
        else:
            echo_pair('Status', stack.stack_status,
                      value_style=STACK_STATUS_TO_COLOR[stack.stack_status],
                      indent=2)
