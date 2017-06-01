# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '13/01/2017'

import click

from ..utils import boto3_exception_handler, pretty_print_config, \
    pretty_print_stack, echo_pair, CHANGESET_STATUS_TO_COLOR, ACTION_TO_COLOR
from ...cli import changeset
from ...config import load_stack_config


@changeset.command(name='list')
@click.argument('config_file', type=click.Path(exists=True))
@click.pass_context
@boto3_exception_handler
def list_(ctx, config_file):
    """List all active change set for a stack.

    \b
    CONFIG_FILE         Stack configuration file.
    """
    session = ctx.obj['session']

    # load config
    stack_config = load_stack_config(config_file)
    pretty_print_config(stack_config)

    # connect co cfn
    region = stack_config.pop('Region')
    cfn = session.resource('cloudformation', region_name=region)
    stack = cfn.Stack(stack_config['StackName'])

    stack_id = stack.stack_id
    pretty_print_stack(stack)

    client = session.client('cloudformation', region_name=region)
    result = client.list_change_sets(StackName=stack_id)

    echo_pair('ChangeSets')

    for summary in result['Summaries']:

        echo_pair(summary['ChangeSetName'], indent=2, sep='')
        echo_pair('ARN', summary['ChangeSetId'], indent=4)

        if 'Description' in summary:
            echo_pair('ChangeSet Description', summary['Description'],
                      indent=4)
        echo_pair('Execution Status', summary['ExecutionStatus'],
                  value_style=CHANGESET_STATUS_TO_COLOR[
                      summary['ExecutionStatus']],
                  indent=4)
        echo_pair('ChangeSet Status', summary['Status'],
                  value_style=CHANGESET_STATUS_TO_COLOR[summary['Status']],
                  indent=4)
        if 'StatusReason' in summary:
            echo_pair('Status Reason', summary['StatusReason'], indent=4)
