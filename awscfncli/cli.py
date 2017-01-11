#!/usr/bin/env python
#  -*- encoding: utf-8 -*-

from __future__ import with_statement

"""Simple CloudFormation Stack Management Tool"""

from functools import wraps
import os

import click
import botocore.exceptions
import boto3

from .events import tail_stack_events, start_tail_stack_events_daemon
from .config import load_stack_config


#
# Helpers
#
def boto3_exception_handler(f):
    """Pretty print boto exceptions."""

    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except (botocore.exceptions.ClientError,
                botocore.exceptions.WaiterError) as e:
            click.echo(click.style(str(e), fg='red'))
        except KeyboardInterrupt as e:
            click.echo(click.style('Aborted.', fg='red'))

    return wrapper


def echo_pair(k, v=None, indent=0):
    click.echo(click.style(' ' * indent + k, bold=True), nl=False)
    if v is not None:
        click.echo(v)
    else:
        click.echo('')


def pretty_print_config(config):
    echo_pair('Region: ', config['Region'])
    echo_pair('Stack Name: ', config['StackName'])
    click.echo(config['StackName'])
    if 'TemplateBody' in config:
        template = os.path.abspath(config['TemplateBody'])
    elif 'TemplateURL' in config:
        template = config['TemplateURL']
    else:
        template = ''
    echo_pair('Template: ', template)


def pretty_print_stack(stack, detail=0):
    echo_pair('Stack ID: ', stack.stack_id)
    if detail == 0:
        return
    echo_pair('Name: ', stack.stack_name)
    echo_pair('Description: ', stack.description)
    echo_pair('Status: ', stack.stack_status)
    echo_pair('Status Reason: ', stack.stack_status_reason)
    echo_pair('Created: ', stack.creation_time)
    echo_pair('Capabilities: ', stack.capabilities)
    if stack.parameters:
        echo_pair('Parameters:')
        for p in stack.parameters:
            echo_pair('%s: ' % p['ParameterKey'], p['ParameterValue'], indent=2)
    if stack.outputs:
        echo_pair('Outputs:')
        for o in stack.outputs:
            echo_pair('%s: ' % o['OutputKey'], o['OutputValue'], indent=2)
    if stack.tags:
        echo_pair('Tags:')
        for t in stack.tags:
            echo_pair('%s: ' % t['Key'], t['Value'], indent=2)


CANNED_STACK_POLICIES = {
    'ALLOW_ALL': '''
{
  "Statement" : [
    {
      "Effect" : "Allow",
      "Action" : "Update:*",
      "Principal": "*",
      "Resource" : "*"
    }
  ]
}
''',
    'ALLOW_MODIFY': '''
{
  "Statement" : [
    {
      "Effect" : "Deny",
       "Action" : ["Update:Replace", "Update:Delete"],
      "Principal": "*",
      "Resource" : "*"
    }
  ]
}
''',
    'DENY_DELETE': '''
{
  "Statement" : [
    {
      "Effect" : "Deny",
      "Action" : "Update:Delete",
      "Principal": "*",
      "Resource" : "*"
    }
  ]
}
''',
    'DENY_ALL': '''
{
  "Statement" : [
    {
      "Effect" : "Deny",
      "Action" : "Update:*",
      "Principal": "*",
      "Resource" : "*"
    }
  ]
}
''',

}


#
# Click CLI
#
@click.group()
@click.pass_context
@click.version_option()
def cli(ctx):
    """Welcome to the CloudFormation Stack Management Command Line Interface."""
    ctx.obj = dict()


@cli.group()
@click.pass_context
def stack(ctx):
    """Stack commands"""
    click.echo('CloudFormation Stack')


@stack.command()
@click.argument('config_file', type=click.Path(exists=True))
@click.option('--no-wait', is_flag=True, default=False,
              help='Wait and print stack events until stack delete is complete.')
@click.option('--on-failure',
              type=click.Choice(['DO_NOTHING', 'ROLLBACK', 'DELETE']),
              default=None,
              help='Determines what action will be taken if stack creation '
                   'fails. This must be one of: DO_NOTHING, ROLLBACK, or '
                   'DELETE. Note setting this option overwrites "OnFailure" '
                   'and "DisableRollback" in the stack configuration file.')
@click.option('--canned-policy',
              type=click.Choice(['ALLOW_MODIFY',
                                 'DENY_DELETE', 'DENY_ALL', ]),
              default=None,
              help='Attach a predefined Stack Policy as StackPolicyBody when '
                   'deploying the stack.  A Stack Policy controls whether '
                   'change to stack resources are allowed during stack update.  '
                   'Valid canned policy are: \b\n'
                   'DENY_DELETE: Allows modify and replace, denys delete\n'
                   'ALLOW_MODIFY: Allows modify, denys replace and delete\n'
                   'DENY_ALL: Denys all updates\n'
                   'Note setting this option overwrites "PolicyBody" and '
                   '"PolicyURL" in the stack configuration file.')
@click.pass_context
@boto3_exception_handler
def deploy(ctx, config_file, no_wait, on_failure, canned_policy):
    """Deploy a new stack using specified stack configuration file"""
    # load config
    stack_config = load_stack_config(config_file)
    pretty_print_config(stack_config)
    click.echo('Deploying stack...')

    # option handling
    if on_failure is not None:
        stack_config.pop('DisableRollback', None)
        stack_config['OnFailure'] = on_failure

    if canned_policy is not None:
        stack_config.pop('StackPolicyURL', None)
        stack_config['StackPolicyBody'] = CANNED_STACK_POLICIES[canned_policy]

    # connect to cfn
    region = stack_config.pop('Region')
    cfn = boto3.resource('cloudformation', region_name=region)

    # create stack
    stack = cfn.create_stack(**stack_config)
    stack_id = stack.stack_id
    pretty_print_stack(stack)

    # exit immediately
    if no_wait:
        return

    # start event tailing
    start_tail_stack_events_daemon(stack, latest_events=0)

    # wait until update complete
    waiter = boto3.client('cloudformation', region_name=region).get_waiter(
        'stack_create_complete')
    waiter.wait(StackName=stack_id)

    click.echo(click.style('Stack deployment complete.', fg='green'))


@stack.command()
@click.argument('config_file', type=click.Path(exists=True))
@click.option('--no-wait', is_flag=True, default=False,
              help='Wait and print stack events until stack delete is complete.')
@click.pass_context
@boto3_exception_handler
def delete(ctx, config_file, no_wait):
    """Delete the stack specified in the configuration file"""
    # load config
    stack_config = load_stack_config(config_file)
    pretty_print_config(stack_config)
    click.echo('Deleting stack...')

    # connect co cfn
    region = stack_config.pop('Region')
    cfn = boto3.resource('cloudformation', region_name=region)
    stack = cfn.Stack(stack_config['StackName'])
    stack_id = stack.stack_id

    pretty_print_stack(stack)

    # delte the stack
    stack.delete()

    # exit immediately
    if no_wait:
        return

    # start event tailing
    start_tail_stack_events_daemon(stack, latest_events=2)

    # wait until delete complete
    waiter = boto3.client('cloudformation', region_name=region).get_waiter(
        'stack_delete_complete')
    waiter.wait(StackName=stack_id)

    click.echo(click.style('Stack delete complete.', fg='green'))


@stack.command()
@click.argument('config_file', type=click.Path(exists=True))
@click.option('--no-wait', is_flag=True, default=False,
              help='Wait and print stack events until stack delete is complete.')
@click.option('--use-previous-template', is_flag=True, default=False,
              help='Reuse the existing template that is associated with the '
                   'stack that you are updating.')
@click.option('--canned-policy',
              type=click.Choice(['ALLOW_ALL', 'ALLOW_MODIFY',
                                 'DENY_DELETE', 'DENY_ALL', ]),
              default=None,
              help='A predefined Stack Policy as StackPolicyBody when '
                   'updating the stack.  A Stack Policy controls whether '
                   'change to stack resources are allowed during stack update.  '
                   'Valid canned policy are: \b\n'
                   'ALLOW_ALL: Allows all updates\n'
                   'DENY_DELETE: Allows modify and replace, denys delete\n'
                   'ALLOW_MODIFY: Allows modify, denys replace and delete\n'
                   'DENY_ALL: Denys all updates\n'
                   'Note setting this option overwrites "PolicyBody" and '
                   '"PolicyURL" in the stack configuration file.')
@click.option('--override-policy',
              type=click.Choice(['ALLOW_ALL', 'ALLOW_MODIFY',
                                 'DENY_DELETE']),
              default=None,
              help='Temporary overriding stack policy during this update.'
                   'Valid canned policy are: \b\n'
                   'ALLOW_ALL: Allows all updates\n'
                   'DENY_DELETE: Allows modify and replace, denys delete\n'
                   'ALLOW_MODIFY: Allows modify, denys replace and delete\n')
@click.pass_context
@boto3_exception_handler
def update(ctx, config_file, no_wait, use_previous_template,
           canned_policy, override_policy):
    """Update the stack specified in the configuration file"""
    # load config
    stack_config = load_stack_config(config_file)
    pretty_print_config(stack_config)
    click.echo('Updating stack...')

    # connect co cfn
    region = stack_config.pop('Region')
    cfn = boto3.resource('cloudformation', region_name=region)
    stack = cfn.Stack(stack_config['StackName'])

    # remove unused parameters
    stack_config.pop('DisableRollback', None)
    stack_config.pop('OnFailure', None)

    # update parameters
    if use_previous_template:
        stack_config.pop('TemplateBody', None)
        stack_config.pop('TemplateURL', None)
        stack_config['UsePreviousTemplate'] = use_previous_template

    if canned_policy is not None:
        stack_config.pop('StackPolicyURL', None)
        stack_config['StackPolicyBody'] = CANNED_STACK_POLICIES[canned_policy]

    if override_policy is not None:
        click.echo('Overriding stack policy during update...')
        stack_config['StackPolicyDuringUpdateBody'] = \
            CANNED_STACK_POLICIES[override_policy]

    stack_id = stack.stack_id
    pretty_print_stack(stack)

    # update stack
    stack.update(**stack_config)

    # exit immediately
    if no_wait:
        return

    # start event tailing
    start_tail_stack_events_daemon(stack, latest_events=2)

    # wait until update complete
    waiter = boto3.client('cloudformation', region_name=region).get_waiter(
        'stack_update_complete')
    waiter.wait(StackName=stack_id)

    click.echo(click.style('Stack update complete.', fg='green'))


@stack.command()
@click.argument('config_file', type=click.Path(exists=True))
@click.pass_context
@boto3_exception_handler
def validate(ctx, config_file):
    """Validate template specified in the config."""
    click.echo('Validating template...')

    stack_config = load_stack_config(config_file)

    client = boto3.client('cloudformation')

    if 'TemplateBody' in stack_config:
        client.validate_template(
            TemplateBody=stack_config['TemplateBody'],
        )
    elif 'TemplateURL' in stack_config:
        client.validate_template(
            TemplateURL=stack_config['TemplateURL'],
        )
    else:
        assert False
    click.echo('Template validation complete.')


@stack.command()
@click.argument('config_file', type=click.Path(exists=True))
@click.option('--timeout', '-t', type=click.IntRange(min=0, max=3600),
              default=300, help='wait time in seconds before exit')
@click.option('--events', '-n', type=click.IntRange(min=0, max=100),
              default=0,
              help='number of latest stack events, 0 means fetch all'
                   'stack events')
@click.pass_context
@boto3_exception_handler
def tail(ctx, config_file, timeout, events):
    """Print stack events and waiting for update (stop using CTRL+C) """

    stack_config = load_stack_config(config_file)

    cfn = boto3.resource('cloudformation', region_name=stack_config['Region'])
    stack = cfn.Stack(stack_config['StackName'])

    tail_stack_events(stack, latest_events=events, time_limit=timeout)


@stack.command()
@click.argument('config_file', type=click.Path(exists=True))
@click.pass_context
@boto3_exception_handler
def describe(ctx, config_file):
    """Describe stack status, parmeter and output"""

    stack_config = load_stack_config(config_file)

    cfn = boto3.resource('cloudformation', region_name=stack_config['Region'])
    stack = cfn.Stack(stack_config['StackName'])

    pretty_print_stack(stack, detail=100)
