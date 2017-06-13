# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '11/01/2017'

import os
import json
from functools import wraps

import click
import botocore.exceptions
from ..config import ConfigError

from botocore.exceptions import ClientError
from awscli.customizations.cloudformation.s3uploader import S3Uploader
from awscli.customizations.cloudformation.artifact_exporter import Template


def boto3_exception_handler(f):
    """Capture and pretty print exceptions"""

    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except (botocore.exceptions.ClientError,
                botocore.exceptions.WaiterError,
                botocore.exceptions.ParamValidationError,
                ConfigError) as e:
            click.secho(str(e), fg='red')
        except KeyboardInterrupt as e:
            click.secho('Aborted.', fg='red')

    return wrapper


def load_template_body(session, config):
    """Load local template file as TemplateBody"""
    if 'TemplateBody' in config:
        try:
            package = bool(config.get('Package', False))
            if package:
                # Get account id to compose a template bucket name.
                sts = session.client('sts')
                accountid = sts.get_caller_identity()["Account"]

                bucket_name = 'awscfncli-%s-%s' % (accountid, config['Region'])
                s3 = session.client('s3')

                try:
                    s3.head_bucket(Bucket=bucket_name)
                except ClientError as e:
                    if e.response['Error']['Code'] == '404':
                        if config['Region'] != 'us-east-1':
                            s3.create_bucket(
                                Bucket=bucket_name,
                                CreateBucketConfiguration={
                                    'LocationConstraint': config['Region']
                                }
                            )
                        else:
                            s3.create_bucket(
                                Bucket=bucket_name
                            )

                        click.echo(
                            'Created bucket %s !' % bucket_name)

                    else:
                        raise e

                uploader = S3Uploader(
                    s3_client=session.client('s3'),
                    bucket_name=bucket_name,
                    region=config['Region'],
                    prefix=config['StackName']
                )
                click.echo(
                    'Set bucket "%s" for storing temporary templates' % bucket_name)

                template = Template(
                    os.path.basename(config['TemplateBody']),
                    os.path.dirname(os.path.realpath(config['TemplateBody'])),
                    uploader)

                exported_template = json.dumps(template.export(), indent=2)

                # Patch s3 endpoint in china region
                if config['Region'].startswith('cn-'):
                    click.echo('Patching s3 endpoint in china region')
                    exported_template = exported_template.replace(
                        's3-cn-north-1.amazonaws.com',
                        's3.cn-north-1.amazonaws.com.cn',
                    )

                config['TemplateBody'] = exported_template
            else:
                with open(config['TemplateBody']) as fp:
                    config['TemplateBody'] = fp.read()

        except Exception as e:
            raise ConfigError(str(e))


def custom_paginator(f, l, **kwargs):
    """Simple custom paginator for those can_pageniate() returns false
    :param f: API function
    :param l: name of the list object to paginate
    :param kwargs: Args passes to the API function
    :return: iterator of result object
    """
    next_token = None
    while True:

        if next_token is None:
            # boto3 does not accept f(NextToken=None)
            r = f(**kwargs)
        else:
            r = f(NextToken=next_token, **kwargs)

        for i in r[l]:
            yield i

        try:
            next_token = r['NextToken']
        except KeyError:
            break


def echo_pair(key, value=None, indent=0,
              value_style=None, key_style=None,
              sep=': '):
    """Pretty print a key value pair

    :param key: The key
    :param value: The value
    :param indent: Number of leading spaces
    :param value_style: click.style parameters of value as a dict, default is none
    :param key_style:  click.style parameters of value as a dict, default is bold text
    :param sep: separator between key and value
    """
    assert key
    key = ' ' * indent + key + sep
    if key_style is None:
        click.secho(key, bold=True, nl=False)
    else:
        click.secho(key, nl=False, **key_style)

    if value is None:
        click.echo('')
    else:

        if value_style is None:
            click.echo(value)
        else:
            click.secho(value, **value_style)


def pretty_print_config(config):
    """Pretty print stack config"""
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
    """Pretty print stack status"""
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


#
# Canned stack policies (used in stack commands)
#
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
      "Effect" : "Allow",
      "Action" : ["Update:Modify"],
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
      "Effect" : "Allow",
      "NotAction" : "Update:Delete",
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
# Status string to click.style parameters
#
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
    'Remove': dict(fg='red', bold=True, reverse=True),
}
