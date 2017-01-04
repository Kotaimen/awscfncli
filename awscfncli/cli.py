#!/usr/bin/env python
#  -*- encoding: utf-8 -*-

from __future__ import with_statement

"""Simple CloudFormation Stack Management Tool"""

import yaml
import click
import boto3
import botocore.exceptions
import time
import threading
import pprint
import colorama
import six

__author__ = 'kotaimen'
__date__ = '31/12/2016'

#
# Helpers
#

STATUS_TO_COLOR = {
    'CREATE_IN_PROGRESS': colorama.Fore.YELLOW,
    'CREATE_FAILED': colorama.Fore.RED,
    'CREATE_COMPLETE': colorama.Fore.GREEN,
    'ROLLBACK_IN_PROGRESS': colorama.Fore.YELLOW,
    'ROLLBACK_FAILED': colorama.Fore.RED,
    'ROLLBACK_COMPLETE': colorama.Fore.GREEN,
    'DELETE_IN_PROGRESS': colorama.Fore.YELLOW,
    'DELETE_FAILED': colorama.Fore.RED,
    'DELETE_SKIPPED': colorama.Fore.YELLOW,
    'DELETE_COMPLETE': colorama.Fore.GREEN,
    'UPDATE_IN_PROGRESS': colorama.Fore.YELLOW,
    'UPDATE_COMPLETE_CLEANUP_IN_PROGRESS': colorama.Fore.YELLOW,
    'UPDATE_COMPLETE': colorama.Fore.GREEN,
    'UPDATE_ROLLBACK_IN_PROGRESS': colorama.Fore.YELLOW,
    'UPDATE_ROLLBACK_FAILED': colorama.Fore.RED,
    'UPDATE_ROLLBACK_COMPLETE_CLEANUP_IN_PROGRESS': colorama.Fore.YELLOW,
    'UPDATE_ROLLBACK_COMPLETE': colorama.Fore.GREEN,
    'UPDATE_FAILED': colorama.Fore.RED,
    'REVIEW_IN_PROGRESS': colorama.Fore.BLUE,
}


def tail_stack_events(client, stack_id, refresh_interval=5):
    seen_events = set()

    while True:
        try:
            # XXX: Handle "next_token"
            response = client.describe_stack_events(StackName=stack_id)
        except botocore.exceptions.ClientError as e:
            click.echo(colorama.Fore.RED + e.message + colorama.Fore.RESET)
            break

        for e in reversed(response['StackEvents']):
            if e['EventId'] in seen_events:
                continue
            seen_events.add(e['EventId'])

            # datetime
            timestamp = e['Timestamp'].strftime('%x %X')
            click.echo('%s - ' % timestamp, nl=False)

            # resource status
            status = e['ResourceStatus']
            click.echo(STATUS_TO_COLOR[status] +
                       status + colorama.Fore.RESET, nl=False)

            # resource id
            click.echo(' - %(LogicalResourceId)s (%(ResourceType)s)' % e,
                       nl=False)

            # description
            if 'ResourceStatusReason' in e:
                click.echo(' - %(ResourceStatusReason)s' % e)
            elif e['PhysicalResourceId']:
                click.echo(' - %(PhysicalResourceId)s' % e)
            else:
                click.echo('')

        time.sleep(refresh_interval)


def tail_stack_events_daemon(client, stack_id):
    thread = threading.Thread(target=tail_stack_events, args=(client, stack_id))
    thread.daemon = True
    thread.start()


def echo_pair(key, msg=None, style=colorama.Style.BRIGHT):
    click.echo(style + key + colorama.Style.RESET_ALL, nl=False)
    if msg:
        click.echo(msg)
    else:
        click.echo('')


def normalize(v):
    if isinstance(v, bool):
        return 'true' if v else 'false'
    elif isinstance(v, int):
        return str(v)
    else:
        return v


#
# Click CLI
#
@click.group(chain=False)
@click.argument('config', type=click.File('r'))
@click.pass_context
def cli(ctx, config):
    """Simple CloudFormation Stack Management Tool

    CONFIG - YAML stack configuration file:

    \b
        Stack:
          template:     template/Ubuntu.template
          region:       region
          name:         stack_name
        Tags:
          tag_key1:      tag_value
          tag_key2:      tag_value
        Parameters:
          param_key1:    param_value1
          param_key2:    param_value2

    """
    ctx.obj = dict()

    config = yaml.safe_load(config)

    # load template
    # XXX: Add support for S3 template and automatic upload
    with open(config['Stack']['template']) as f:
        template_body = f.read()

    # generate parameters

    if 'Parameters' in config:
        template_parameters = list(
            {'ParameterKey': k, 'ParameterValue': normalize(v)}
            for k, v in six.iteritems(config['Parameters'])
        )
    else:
        template_parameters = []

    # generate tags
    if 'Tags' in config:
        tags = list(
            {'Key': k, 'Value': v}
            for k, v in six.iteritems(config['Tags'])
        )
    else:
        tags = []

    # set context object
    ctx.obj['region'] = config['Stack']['region']
    ctx.obj['stack_name'] = config['Stack']['name']
    ctx.obj['template_body'] = template_body
    ctx.obj['template_parameters'] = template_parameters
    ctx.obj['tags'] = tags

    echo_pair('Stack Name: ', config['Stack']['name'])
    echo_pair('Template Location: ', config['Stack']['template'])


@cli.command()
@click.pass_context
def validate(ctx):
    """Validate template specified in the config"""
    click.echo('Validating stack...')
    client = boto3.client(
        'cloudformation',
        region_name=ctx.obj['region']
    )
    try:
        response = client.validate_template(
            TemplateBody=ctx.obj['template_body'],
        )
    except botocore.exceptions.ClientError as e:
        click.echo(colorama.Fore.RED + e.message + colorama.Fore.RESET)
    else:
        click.echo('Validation complete.')


@cli.command()
@click.pass_context
def deploy(ctx):
    """Deploy a new stack"""
    client = boto3.client(
        'cloudformation',
        region_name=ctx.obj['region']
    )

    click.echo('Deploying stack...')
    try:
        response = client.create_stack(
            StackName=ctx.obj['stack_name'],
            TemplateBody=ctx.obj['template_body'],
            Parameters=ctx.obj['template_parameters'],
            Capabilities=['CAPABILITY_IAM'],
            OnFailure='DO_NOTHING',
            Tags=ctx.obj['tags']
        )

        stack_id = response['StackId']
        tail_stack_events_daemon(client, stack_id)

        waiter = client.get_waiter('stack_create_complete')
        waiter.wait(StackName=ctx.obj['stack_name'])
    except (botocore.exceptions.ClientError,
            botocore.exceptions.WaiterError)  as e:
        click.echo(colorama.Fore.RED + e.message + colorama.Fore.RESET)
    else:
        click.echo('Stack creation complete.')


@cli.command()
@click.pass_context
def update(ctx):
    """Update existing stack"""
    client = boto3.client(
        'cloudformation',
        region_name=ctx.obj['region']
    )

    click.echo('Updating stack...')
    try:
        response = client.update_stack(
            StackName=ctx.obj['stack_name'],
            TemplateBody=ctx.obj['template_body'],
            Parameters=ctx.obj['template_parameters'],
            Capabilities=['CAPABILITY_IAM'],
            Tags=ctx.obj['tags']
        )

        stack_id = response['StackId']
        tail_stack_events_daemon(client, stack_id)

        waiter = client.get_waiter('stack_update_complete')
        waiter.wait(StackName=ctx.obj['stack_name'])

    except (botocore.exceptions.ClientError,
            botocore.exceptions.WaiterError)  as e:
        click.echo(colorama.Fore.RED + e.message + colorama.Fore.RESET)
    else:
        click.echo('Stack update complete.')


@cli.command()
@click.pass_context
def delete(ctx):
    """Delete existing stack"""
    client = boto3.client(
        'cloudformation',
        region_name=ctx.obj['region']
    )

    click.echo('Deleting stack...')
    try:
        client.delete_stack(StackName=ctx.obj['stack_name'])

        tail_stack_events_daemon(client, ctx.obj['stack_name'])

        waiter = client.get_waiter('stack_delete_complete')
        waiter.wait(StackName=ctx.obj['stack_name'])
    except (botocore.exceptions.ClientError,
            botocore.exceptions.WaiterError)  as e:
        click.echo(colorama.Fore.RED + e.message + colorama.Fore.RESET)
    else:
        click.echo('Stack deletion complete.')


@cli.command()
@click.pass_context
def describe(ctx):
    """Describe stack status, parameter and output"""
    client = boto3.client(
        'cloudformation',
        region_name=ctx.obj['region']
    )
    try:
        response = client.describe_stacks(StackName=ctx.obj['stack_name'])
    except botocore.exceptions.ClientError as e:
        click.echo(colorama.Fore.RED + e.message + colorama.Fore.RESET)
    else:
        for stack in response['Stacks']:
            echo_pair('Stack ID: ', stack['StackId'])
            echo_pair('Description: ', stack['Description'])
            echo_pair('Status: ',
                      STATUS_TO_COLOR[stack['StackStatus']] + \
                      stack['StackStatus'] + colorama.Fore.RESET)
            if 'Reason' in stack:
                echo_pair('Reason: ', stack['StackStatusReason'])
            if 'Parameters' in stack:
                echo_pair('Parameters:')
                for p in stack['Parameters']:
                    echo_pair('  - %s: ' % p['ParameterKey'],
                              p['ParameterValue'])
            if 'Outputs' in stack:
                echo_pair('Outputs:')
                for o in stack['Outputs']:
                    echo_pair('  - %s: ' % o['OutputKey'], o['OutputValue'])


@cli.command()
@click.pass_context
def tail(ctx):
    """Tail stack events (stop using CTRL+C) """
    client = boto3.client(
        'cloudformation',
        region_name=ctx.obj['region']
    )
    tail_stack_events(client, ctx.obj['stack_name'], refresh_interval=15)
