#  -*- encoding: utf-8 -*-

import click
import botocore.exceptions

from . import stack
from ..utils import boto3_exception_handler, \
    pretty_print_stack, custom_paginator, echo_pair, ContextObject, \
    STACK_STATUS_TO_COLOR


@stack.command()
@click.option('--stack-resources', '-r', is_flag=True, default=False,
              help='Display stack resources.')
@click.option('--stack-exports', '-e', is_flag=True, default=False,
              help='Display stack exports.')
@click.pass_context
@boto3_exception_handler
def describe(ctx, stack_resources, stack_exports):
    """Describe stack status and information"""
    assert isinstance(ctx.obj, ContextObject)

    for stack_config in ctx.obj.stacks:
        echo_pair(stack_config['Metadata']['QualifiedName'],
                  key_style=dict(bold=True), sep='')

        describe_one(ctx, stack_config, stack_resources, stack_exports)


def describe_one(ctx, stack_config, stack_resources, stack_exports):
    """Describe stack status and information"""
    assert isinstance(ctx.obj, ContextObject)

    session = ctx.obj.get_boto3_session(stack_config)
    region = stack_config['Metadata']['Region']

    cloudformation = session.resource(
        'cloudformation',
        region_name=region
    )

    stack = cloudformation.Stack(stack_config['StackName'])

    try:
        stack.stack_status
    except botocore.exceptions.ClientError as e:
        click.secho(str(e), fg='red')
        return

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
                                region_name=region)
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
