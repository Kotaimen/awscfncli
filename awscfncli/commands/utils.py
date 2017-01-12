# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '11/01/2017'

import os
from functools import wraps

import click
import botocore.exceptions


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

    if detail == 0: return
    echo_pair('Name: ', stack.stack_name)
    echo_pair('Description: ', stack.description)

    click.echo(click.style('Status: ', bold=True), nl=False)
    click.echo(click.style(stack.stack_status, **STATUS_TO_COLOR[stack.stack_status]))

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

    if detail <= 1: return
    echo_pair('Resources:')
    for r in stack.resource_summaries.all():
        echo_pair('Logical ID: ', r.logical_resource_id, indent=2)
        echo_pair('Type: ', r.resource_type, indent=4)
        echo_pair('Physical ID: ', r.physical_resource_id, indent=4)
        echo_pair('Last Updated: ', r.last_updated_timestamp, indent=4)


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

STATUS_TO_COLOR = {
    'CREATE_IN_PROGRESS': dict(fg='yellow'),
    'CREATE_FAILED': dict(fg='red'),
    'CREATE_COMPLETE': dict(fg='green'),
    'ROLLBACK_IN_PROGRESS': dict(fg='yellow'),
    'ROLLBACK_FAILED': dict(fg='red'),
    'ROLLBACK_COMPLETE': dict(fg='red'),
    'DELETE_IN_PROGRESS': dict(fg='yellow'),
    'DELETE_FAILED': dict(fg='red'),
    'DELETE_SKIPPED': dict(fg='white', dim=True),
    'DELETE_COMPLETE': dict(fg='white', dim=True),
    'UPDATE_IN_PROGRESS': dict(fg='yellow'),
    'UPDATE_COMPLETE_CLEANUP_IN_PROGRESS': dict(fg='green'),
    'UPDATE_COMPLETE': dict(fg='green'),
    'UPDATE_ROLLBACK_IN_PROGRESS': dict(fg='red'),
    'UPDATE_ROLLBACK_FAILED': dict(fg='red'),
    'UPDATE_ROLLBACK_COMPLETE_CLEANUP_IN_PROGRESS': dict(fg='red'),
    'UPDATE_ROLLBACK_COMPLETE': dict(fg='green'),
    'UPDATE_FAILED': dict(fg='red'),
    'REVIEW_IN_PROGRESS': dict(fg='yellow', dim=True),
}
