#!/usr/bin/env python
#  -*- encoding: utf-8 -*-

from __future__ import with_statement

"""Simple CloudFormation Stack Management Tool"""

from functools import wraps

import click
import botocore.exceptions
import boto3

from .events import tail_stack_events
from .config import load_stack_config


def boto3_exception_handler(f):
    """Pretty print boto exceptions."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            f(*args, **kwargs)
        except (botocore.exceptions.ClientError,
                botocore.exceptions.WaiterError) as e:
            click.echo(click.style(e.message, fg='red'))
        else:
            click.echo('Stack creation complete.')

    return wrapper


#
# Click CLI
#
@click.group(chain=False)
@click.pass_context
def cli(ctx):
    """Simple CloudFormation Stack Management Tool

    """
    ctx.obj = dict()


@cli.command()
@click.argument('config_file', type=click.Path(exists=True))
@click.pass_context
@boto3_exception_handler
def validate(ctx, config_file):
    """Validate template specified in the config."""

    stack_config = load_stack_config(config_file)

    client = boto3.client('cloudformation')
    client.validate_template(TemplateBody=stack_config['TemplateBody'])

    click.echo('validate')


@cli.command()
@click.argument('config_file', type=click.Path(exists=True))
@click.option('--timeout', '-t', type=click.IntRange(min=0, max=3600),
              default=300, help='timeout in seconds')
@click.option('--events', '-n', type=click.IntRange(min=0, max=100),
              default=0,
              help='number of latest stack events to display, 0 means ')
@click.pass_context
@boto3_exception_handler
def tail(ctx, config_file, timeout, events):
    """Tail stack events (stop using CTRL+C) """

    stack_config = load_stack_config(config_file)

    cfn = boto3.resource('cloudformation', region_name=stack_config['Region'])
    stack = cfn.Stack(stack_config['StackName'])

    tail_stack_events(stack, latest_events=events, time_limit=timeout)
