# -*- encoding: utf-8 -*-

import uuid

import botocore.exceptions
import click

from . import stack
from ..utils import boto3_exception_handler, ContextObject
from ..utils import echo_pair, pretty_print_config, echo_pair_if_exists, \
    CHANGESET_STATUS_TO_COLOR, ACTION_TO_COLOR
from ..utils import run_packaging
from ..utils import start_tail_stack_events_daemon


@stack.command()
@click.option('--confirm', is_flag=True, default=False)
@click.option('--use-previous-template', is_flag=True, default=False,
              help='Reuse the existing template that is associated with the '
                   'stack that you are updating.')
@click.pass_context
@boto3_exception_handler
def sync(ctx, confirm, use_previous_template):
    """Create and execute ChangeSets (SAM)

    Combines "aws cloudformation package" and "aws cloudformation deploy" command
    into one.  If the stack is not created yet, a CREATE type ChangeSet is created,
    otherwise UPDATE ChangeSet is created.

    """
    assert isinstance(ctx.obj, ContextObject)

    for qualified_name, stack_config in ctx.obj.stacks.items():
        session = ctx.obj.get_boto3_session(stack_config)
        pretty_print_config(qualified_name, stack_config, session,
                            ctx.obj.verbosity)
        sync_one(ctx, session, stack_config, confirm, use_previous_template)


def sync_one(ctx, session, stack_config, confirm, use_previous_template):
    # package the template
    if use_previous_template:
        stack_config.pop('TemplateBody', None)
        stack_config.pop('TemplateURL', None)
        stack_config['UsePreviousTemplate'] = use_previous_template
    else:
        run_packaging(stack_config, session, ctx.obj.verbosity)

    # connect to cloudformation client
    client = session.client('cloudformation')

    # pop metadata form stack config
    stack_config.pop('Metadata')

    # generate a unique changeset name
    changeset_name = '%s-%s' % \
                     (stack_config['StackName'], str(uuid.uuid1()))

    # prepare stack config
    stack_config['ChangeSetName'] = changeset_name
    click.echo('Generated ChangeSet name {}'.format(changeset_name))

    try:
        # check whether stack is already created.
        status = client.describe_stacks(StackName=stack_config['StackName'])
        stack_status = status['Stacks'][0]['StackStatus']
    except botocore.exceptions.ClientError as e:
        # stack not yet created
        is_new_stack = True
        changeset_type = 'CREATE'
    else:
        if stack_status == 'REVIEW_IN_PROGRESS':
            # first ChangeSet execution failed, create "new stack" changeset again
            is_new_stack = True
            changeset_type = 'CREATE'
        else:
            # updating an existing stack
            is_new_stack = False
            changeset_type = 'UPDATE'

    stack_config['ChangeSetType'] = changeset_type
    stack_config.pop('StackPolicyBody', None)
    stack_config.pop('StackPolicyURL', None)
    termination_protection = stack_config.pop(
        'EnableTerminationProtection', None)

    # create changeset
    echo_pair('ChangeSet Type', changeset_type)
    result = client.create_change_set(**stack_config)

    # termination protection should be set after the creation of stack
    # or changeset
    if result and 'Id' in result and termination_protection is not None:
        click.secho(
            'Setting Termination Protection to "%s"' %
            termination_protection, fg='red')
        client.update_termination_protection(
            EnableTerminationProtection=termination_protection,
            StackName=stack_config['StackName']
        )

    echo_pair('ChangeSet ARN', result['Id'])

    # wait until changeset is created
    waiter = client.get_waiter('change_set_create_complete')
    try:
        waiter.wait(ChangeSetName=result['Id'])
    except botocore.exceptions.WaiterError as e:
        click.secho('ChangeSet create failed.', fg='red')
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

    if result['Status'] not in ('AVAILABLE', 'CREATE_COMPLETE'):
        click.secho('ChangeSet not executable.', fg='red')
        return

    if is_new_stack:
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
    cloudformation = session.resource('cloudformation')
    stack = cloudformation.Stack(stack_config['StackName'])
    # pretty_print_stack(stack)

    # start event tailing
    start_tail_stack_events_daemon(session, stack)

    # wait until update complete
    waiter = client.get_waiter(waiter_model)
    waiter.wait(StackName=stack.stack_id)

    click.secho('ChangSet execution complete.', fg='green')
