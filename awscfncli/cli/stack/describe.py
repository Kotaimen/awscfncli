#  -*- encoding: utf-8 -*-

import click
import botocore.exceptions

from . import stack
from ..utils import boto3_exception_handler, ContextObject, \
    pretty_print_config, pretty_print_stack, custom_paginator, echo_pair, \
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

    for qualified_name, stack_config in ctx.obj.stacks.items():
        session = ctx.obj.get_boto3_session(stack_config)
        pretty_print_config(qualified_name, stack_config, session,
                            ctx.obj.verbosity)
        describe_one(ctx, session, stack_config, stack_resources, stack_exports)


def describe_one(ctx, session, stack_config, stack_resources, stack_exports):
    """Describe stack status and information"""
    assert isinstance(ctx.obj, ContextObject)

    cloudformation = session.resource('cloudformation')

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
        client = session.client('cloudformation',)
        echo_pair('Exports')
        for export in custom_paginator(client.list_exports, 'Exports'):

            if export['ExportingStackId'] == stack.stack_id:
                echo_pair(export['Name'], export['Value'], indent=2)
                try:
                    for import_ in custom_paginator(client.list_imports,
                                                    'Imports',
                                                    ExportName=export['Name']):
                        echo_pair('Imported By', import_,
                                  value_style=dict(fg='red'), indent=4)
                except botocore.exceptions.ClientError as e:
                    echo_pair('Export not used by any stack.',
                              key_style=dict(fg='green'), indent=4, sep='')
