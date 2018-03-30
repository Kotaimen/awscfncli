# -*- encoding: utf-8 -*-

import uuid
import click

import botocore.exceptions

from . import changeset
from ..utils import boto3_exception_handler, \
    echo_pair, ContextObject, \
    CHANGESET_STATUS_TO_COLOR, ACTION_TO_COLOR
from ..utils import start_tail_stack_events_daemon
from ..utils import package_template, is_local_path


def echo_pair_if_exists(d, k, v, indent=2, key_style=None, value_style=None):
    if v in d:
        echo_pair(k, d[v], indent=indent,
                  key_style=key_style, value_style=value_style, )


@changeset.command()
@click.option('--confirm', is_flag=True, default=False)
@click.option('--use-previous-template', is_flag=True, default=False,
              help='Reuse the existing template that is associated with the '
                   'stack that you are updating.')
@click.pass_context
@boto3_exception_handler
def sync(ctx, confirm, use_previous_template):
    """Create a changeset and execute it immediately"""
    assert isinstance(ctx.obj, ContextObject)

    for stack_config in ctx.obj.stacks:
        click.secho(
            'Working on stack %s.%s' % \
            (stack_config['Metadata']['StageName'], stack_config['StackName']),
            bold=True)
        sync_one(ctx, stack_config, confirm, use_previous_template)

def sync_one(ctx, stack_config, confirm, use_previous_template):

    session = ctx.obj.get_boto3_session(stack_config)
    region = stack_config['Metadata']['Region']
    package = stack_config['Metadata']['Package']
    artifact_store = stack_config['Metadata']['ArtifactStore']

    client = session.client(
        'cloudformation',
        region_name=region
    )

    # pop metadata form stack config
    metadata = stack_config.pop('Metadata')

    # generate a unique changeset name
    changeset_name = '%s-%s' % \
                     (stack_config['StackName'], str(uuid.uuid1()))

    # prepare stack config
    stack_config['ChangeSetName'] = changeset_name
    click.echo('Generated ChangeSet name {}'.format(changeset_name))

    if use_previous_template:
        stack_config.pop('TemplateBody', None)
        stack_config.pop('TemplateURL', None)
        stack_config['UsePreviousTemplate'] = use_previous_template
    else:
        if package and 'TemplateURL' in stack_config:
            template_path = stack_config.get('TemplateURL')
            if not is_local_path(template_path):
                packaged_template = package_template(
                    session,
                    template_path,
                    bucket_region=region,
                    bucket_name=artifact_store,
                    prefix=stack_config['StackName'])
                stack_config['TemplateBody'] = packaged_template
                stack_config.pop('TemplateURL')

    try:
        client.describe_stacks(StackName=stack_config['StackName'])
    except botocore.exceptions.ClientError as e:
        # except Exception as e:
        changeset_type = 'CREATE'
    else:
        changeset_type = 'UPDATE'

    stack_config['ChangeSetType'] = changeset_type

    stack_config.pop('StackPolicyBody', None)
    stack_config.pop('StackPolicyURL', None)

    # create changeset
    echo_pair('ChangeSet Type', changeset_type)
    result = client.create_change_set(**stack_config)
    echo_pair('ChangeSet ARN', result['Id'])

    # wait until changeset is created
    waiter = client.get_waiter('change_set_create_complete')
    try:
        waiter.wait(ChangeSetName=result['Id'])
    except botocore.exceptions.WaiterError as e:
        # click.secho('ChangeSet create failed.', fg='red')
        pass
    else:
        click.secho('ChangeSet create complete.', fg='green')

    result = client.describe_change_set(
        ChangeSetName=changeset_name,
        StackName=stack_config['StackName'],

    )

    # echo_pair('ChangeSet Name', result['ChangeSetName'])
    # echo_pair_if_exists(result, 'ChangeSet Description', 'Description')
    # echo_pair('Execution Status', result['ExecutionStatus'],
    #           value_style=CHANGESET_STATUS_TO_COLOR[result['ExecutionStatus']])
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

    if result['Status'] != 'AVAILABLE':
        click.secho('ChangeSet not executable.', fg='red')
        return

    if changeset_type == 'CREATE':
        waiter_model = 'stack_create_complete'
    else:
        waiter_model = 'stack_update_complete'

    if confirm:
        click.confirm('Do you want to execute ChangeSet?', abort=True)

    client.execute_change_set(
        ChangeSetName=changeset_name,
        StackName=stack_config['StackName'],
    )
    click.echo('Executing changeset...')

    # get stack resource to wait on changset execution
    cloudformation = session.resource(
        'cloudformation',
        region_name=region
    )
    stack = cloudformation.Stack(stack_config['StackName'])
    # pretty_print_stack(stack)

    # start event tailing
    start_tail_stack_events_daemon(session, stack, latest_events=5)

    # wait until update complete
    waiter = client.get_waiter(waiter_model)
    waiter.wait(StackName=stack.stack_id)

    click.secho('ChangSet execution complete.', fg='green')
