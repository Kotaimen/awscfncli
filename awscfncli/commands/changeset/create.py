# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '12/01/2017'

import uuid

import click

from ..utils import boto3_exception_handler, pretty_print_config, \
    load_template_body, echo_pair
from ..stack.events import start_tail_stack_events_daemon
from ...cli import changeset
from ...config import load_stack_config


@changeset.command()
@click.argument('config_file', type=click.Path(exists=True))
@click.argument('changeset_name', required=False, default=None)
@click.option('--no-wait', is_flag=True, default=False,
              help='Exit immediately after operation is started.')
@click.option('--use-previous-template', is_flag=True, default=False,
              help='Reuse the existing template that is associated with the '
                   'stack that you are updating.')
@click.option('--changeset-type', type=click.Choice(['CREATE', 'UPDATE']),
              default='UPDATE',
              help='The type of change set operation. To create a change set '
                   'for a new stack, specify CREATE. To create a change set '
                   'for an existing stack, specify UPDATE.')
@click.option('--execute', is_flag=True, default=False,
              help='Execute the ChangeSet immediately after its created. '
                   'Specify this disables "--no-wait" option. ')
@click.pass_context
@boto3_exception_handler
def create(ctx, config_file, no_wait, changeset_name, use_previous_template,
           changeset_type, execute):
    """Creates a list of changes for a stack.

    AWS CloudFormation generates the change set by comparing the template's
    information with the information that you submit. A change set can help
    you understand which resources AWS CloudFormation will change, and how
    it will change them, before you update your stack. Change sets allow
    you to check before making a change to avoid deleting or replacing
    critical resources.

    \b
    CONFIG_FILE         Stack configuration file.
    CHANGESET_NAME      The name of the change set. must be unique among all
                        change sets that are associated with the specified
                        stack. cfncli will automatically generate a unique
                        name if one not given.
    """
    session = ctx.obj['session']

    # load config
    stack_config = load_stack_config(config_file)
    pretty_print_config(stack_config)
    load_template_body(session, stack_config)
    click.echo('Creating change set...')

    # connect co cfn
    region = stack_config.pop('Region')

    # remove unused parameters
    stack_config.pop('DisableRollback', None)
    stack_config.pop('OnFailure', None)
    stack_config.pop('Package', None)

    # update parameters
    if changeset_name is None:
        # XXX: use hash of stack config & template as unqiue name?
        changeset_name = '%s-ChangeSet-%s' % (stack_config['StackName'],
                                              str(uuid.uuid1())[:8])
    stack_config['ChangeSetName'] = changeset_name

    echo_pair('ChangeSet Name', changeset_name)
    if use_previous_template:
        stack_config.pop('TemplateBody', None)
        stack_config.pop('TemplateURL', None)
        stack_config['UsePreviousTemplate'] = use_previous_template

    stack_config['ChangeSetType'] = changeset_type

    stack_config.pop('StackPolicyBody', None)
    stack_config.pop('StackPolicyURL', None)

    # create changeset
    client = session.client('cloudformation', region_name=region)
    result = client.create_change_set(**stack_config)
    echo_pair('ChangeSet ARN', result['Id'])

    # exit immediately
    if not execute and no_wait:
        return

    # wait until update complete
    waiter = client.get_waiter(
        'change_set_create_complete')
    waiter.wait(ChangeSetName=result['Id'])

    click.secho('ChangeSet creation complete.', fg='green')

    if not execute:
        return

    if changeset_type == 'CREATE':
        waiter_model = 'stack_create_complete'
    else:
        waiter_model = 'stack_update_complete'

    client.execute_change_set(
        ChangeSetName=changeset_name,
        StackName=stack_config['StackName'],
    )

    # exit immediately
    if no_wait:
        return

    # execute changeset
    cfn = session.resource('cloudformation', region_name=region)
    stack = cfn.Stack(stack_config['StackName'])

    # start event tailing
    start_tail_stack_events_daemon(session, stack, latest_events=5)

    # wait until update complete
    waiter = client.get_waiter(waiter_model)
    waiter.wait(StackName=stack.stack_id)

    click.secho('ChangSet execution complete.',fg='green')
