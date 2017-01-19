# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '11/01/2017'

import os
from functools import wraps

import click
import botocore.exceptions
from ..config import ConfigError


def boto3_exception_handler(f):
    """Pretty print boto exceptions."""

    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except (botocore.exceptions.ClientError,
                botocore.exceptions.WaiterError,
                botocore.exceptions.ParamValidationError,
                ConfigError) as e:
            click.echo(click.style(str(e), fg='red'))
        except KeyboardInterrupt as e:
            click.echo(click.style('Aborted.', fg='red'))

    return wrapper


def load_template_body(config):
    if 'TemplateBody' in config:
        try:
            with open(config['TemplateBody']) as fp:
                config['TemplateBody'] = fp.read()
        except Exception as e:
            raise ConfigError(str(e))


def echo_pair(key, value=None, indent=0, value_style=None, key_style=None,
              sep=': '):
    assert key
    key = ' ' * indent + key + sep
    if key_style is None:
        click.echo(click.style(key, bold=True), nl=False)
    else:
        click.echo(click.style(key, **key_style), nl=False)

    if value is None:
        click.echo('')
    else:

        if value_style is None:
            click.echo(value)
        else:
            click.echo(click.style(value, **value_style))


def pretty_print_config(config):
    echo_pair('Region', config['Region'])
    echo_pair('Stack Name', config['StackName'])
    if 'TemplateBody' in config:
        template = os.path.abspath(config['TemplateBody'])
    elif 'TemplateURL' in config:
        template = config['TemplateURL']
    else:
        template = ''
    echo_pair('Template', template)


def pretty_print_stack(stack, detail=False):
    echo_pair('Stack ID', stack.stack_id)

    if not detail:
        return

    echo_pair('Name', stack.stack_name)
    echo_pair('Description', stack.description)

    echo_pair('Status', stack.stack_status,
              value_style=STACK_STATUS_TO_COLOR[stack.stack_status])
    echo_pair('Created', stack.creation_time)
    if stack.last_updated_time:
        echo_pair('Last Updated', stack.last_updated_time)
    echo_pair('Capabilities', stack.capabilities)

    if stack.parameters:
        echo_pair('Parameters')
        for p in stack.parameters:
            echo_pair(p['ParameterKey'], p['ParameterValue'], indent=2)
    if stack.outputs:
        echo_pair('Outputs')
        for o in stack.outputs:
            echo_pair(o['OutputKey'], o['OutputValue'], indent=2)
    if stack.tags:
        echo_pair('Tags')
        for t in stack.tags:
            echo_pair(t['Key'], t['Value'], indent=2)


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

STACK_STATUS_TO_COLOR = {
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
    'REVIEW_IN_PROGRESS': dict(fg='yellow'),
}

CHANGESET_STATUS_TO_COLOR = {
    'UNAVAILABLE': dict(fg='white', dim=True),
    'AVAILABLE': dict(fg='green'),
    'EXECUTE_IN_PROGRESS': dict(fg='yellow'),
    'EXECUTE_COMPLETE': dict(fg='green'),
    'EXECUTE_FAILED': dict(fg='red'),
    'OBSOLETE': dict(fg='white', dim=True),

    'CREATE_PENDING': dict(fg='white', dim=True),
    'CREATE_IN_PROGRESS': dict(fg='yellow'),
    'CREATE_COMPLETE': dict(fg='green'),
    'DELETE_COMPLETE': dict(fg='white', dim=True),
    'FAILED': dict(fg='red'),
}

ACTION_TO_COLOR = {
    'Add': dict(fg='green', bold=True, reverse=True),
    'Modify': dict(fg='yellow', bold=True, reverse=True),
    'Delete': dict(fg='red', bold=True, reverse=True),
}
