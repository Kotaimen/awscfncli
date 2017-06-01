# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '13/01/2017'

import click

from ..utils import boto3_exception_handler, pretty_print_config, \
    echo_pair, CHANGESET_STATUS_TO_COLOR, ACTION_TO_COLOR
from ...cli import changeset
from ...config import load_stack_config


def echo_pair_if_exists(d, k, v, indent=2):
    if v in d:
        echo_pair(k, d[v], indent=indent)


@changeset.command()
@click.argument('config_file', type=click.Path(exists=True))
@click.argument('changeset_name')
@click.pass_context
@boto3_exception_handler
def describe(ctx, config_file, changeset_name):
    """Print changes in specified change set.

    Returns the inputs for the change set and a list of changes that AWS
    CloudFormation will make if you execute the change set.

    \b
    CONFIG_FILE         Stack configuration file.
    """
    session = ctx.obj['session']

    # load config
    stack_config = load_stack_config(config_file)
    pretty_print_config(stack_config)

    # connect to cfn
    region = stack_config.pop('Region')

    # describe change set
    client = session.client('cloudformation', region_name=region)
    result = client.describe_change_set(
        ChangeSetName=changeset_name,
        StackName=stack_config['StackName'],

    )

    echo_pair('ChangeSet Name', result['ChangeSetName'])

    echo_pair_if_exists(result, 'ChangeSet Description', 'Description')
    echo_pair('Execution Status', result['ExecutionStatus'],
              value_style=CHANGESET_STATUS_TO_COLOR[result['ExecutionStatus']])
    echo_pair('ChangeSet Status', result['Status'],
              value_style=CHANGESET_STATUS_TO_COLOR[result['Status']])
    echo_pair_if_exists(result, 'Status Reason', 'StatusReason')

    echo_pair('Resource Changes')
    for change in result['Changes']:
        echo_pair(change['ResourceChange']['LogicalResourceId'],
                  '(%s)' % change['ResourceChange']['ResourceType'],
                  indent=2, sep=' ')

        echo_pair('Action', change['ResourceChange']['Action'],
                  value_style=ACTION_TO_COLOR[
                      change['ResourceChange']['Action']],
                  indent=4)
        echo_pair_if_exists(change['ResourceChange'],
                            'Physical Resource',
                            'PhysicalResourceId', indent=4)
        echo_pair_if_exists(change['ResourceChange'],
                            'Replacement',
                            'Replacement', indent=4)
        echo_pair_if_exists(change['ResourceChange'],
                            'Scope',
                            'Scope', indent=4)

