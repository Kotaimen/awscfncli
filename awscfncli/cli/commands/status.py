#  -*- encoding: utf-8 -*-

import click
import botocore.exceptions
import yaml

from ..main import cfn_cli
from ..utils import boto3_exception_handler, ContextObject, echo_pair, \
    STACK_STATUS_TO_COLOR


@cfn_cli.command()
@click.option('-d', '--dry-run', is_flag=True, default=False,
              help='Don\'t retrieve stack deployment status (faster).')
@click.pass_context
@boto3_exception_handler
def status(ctx, dry_run):
    """List status of selected stacks."""
    assert isinstance(ctx.obj, ContextObject)

    for qualified_name, stack_config in ctx.obj.stacks.items():
        echo_pair(qualified_name, key_style=dict(bold=True), sep='')
        if ctx.obj.verbosity > 0:
            click.secho(
                yaml.safe_dump(stack_config, default_flow_style=False),
            )
        else:
            echo_pair('Profile', stack_config['Metadata']['Profile'], indent=2)
            echo_pair('Region', stack_config['Metadata']['Region'], indent=2)
            echo_pair('Stack Name', stack_config['StackName'], indent=2)
        if dry_run:
            continue

        session = ctx.obj.get_boto3_session(stack_config)

        cloudformation = session.resource(
            'cloudformation',
            region_name=stack_config['Metadata']['Region']
        )

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
