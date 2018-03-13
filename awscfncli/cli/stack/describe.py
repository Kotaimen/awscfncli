#  -*- encoding: utf-8 -*-

import click
import botocore

from . import stack
from ..utils import boto3_exception_handler, pretty_print_stack, \
    STACK_STATUS_TO_COLOR, custom_paginator, echo_pair, ContextObject


@stack.command()
# XXX: move this logic to a seperate decorator to be shared between subcommands
@click.argument('env_pattern', envvar='CFN_ENV_PATTERN')
@click.argument('stack_pattern', envvar='CFN_STACK_PATTERN')
@click.option('--stack-resources', '-r', is_flag=True, default=False,
              help='Display stack resources.')
@click.option('--stack-exports', '-e', is_flag=True, default=False,
              help='Display stack exports.')
@click.pass_context
@boto3_exception_handler
def describe(ctx, stack_resources, stack_exports, env_pattern, stack_pattern):
    """Print status, parameters, outputs, stack resources and export values
    of the stack specified in the configuration file.
    """
    assert isinstance(ctx.obj, ContextObject)

    stack_config \
        = ctx.obj.find_one_stack_config(env_pattern=env_pattern,
                                        stack_pattern=stack_pattern)

    session = ctx.obj.get_boto3_session(stack_config)

    cloudformation = session.resource(
        'cloudformation',
        region_name=stack_config['Region']
    )

    stack = cloudformation.Stack(stack_config['StackName'])

    pretty_print_stack(stack, detail=True)

    if stack_resources:
        echo_pair('Resources')
        for r in stack.resource_summaries.all():
            echo_pair(r.logical_resource_id,
                      '(%s)' % r.resource_type,
                      indent=2, sep=' ')
            echo_pair('Status', r.resource_status,
                      value_style=STACK_STATUS_TO_COLOR[r.resource_status],
                      indent=4)
            echo_pair('Physical ID', r.physical_resource_id, indent=4)
            echo_pair('Last Updated', r.last_updated_timestamp, indent=4)

    if stack_exports:
        client = session.client('cloudformation',
                                region_name=stack_config['Region'])
        echo_pair('Exports')
        for export in custom_paginator(client.list_exports, 'Exports'):

            if export['ExportingStackId'] == stack.stack_id:
                echo_pair(export['Name'], export['Value'], indent=2)
                try:
                    for import_ in custom_paginator(client.list_imports, 'Imports',
                                                    ExportName=export['Name']):
                        echo_pair('Imported By', import_,
                                  value_style=dict(fg='red'), indent=4)
                except botocore.exceptions.ClientError as e:
                    echo_pair('Export not used by any stack.',
                              key_style=dict(fg='green'), indent=4, sep='')
