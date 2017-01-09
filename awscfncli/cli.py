#!/usr/bin/env python
#  -*- encoding: utf-8 -*-

from __future__ import with_statement

"""Simple CloudFormation Stack Management Tool"""

import click
import boto3

from .events import tail_stack_events
from .config import load_stack_config

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
def validate(ctx, config_file):
    """Validate template specified in the config."""

    client = boto3.client('cloudformation')
    client.validate_template(TemplateBody='')

    # cfn = boto3.resource('cloudformation', region_name='us-east-1')
    # stack = cfn.Stack('')

    click.echo('validate')


@cli.command()
@click.argument('config_file', type=click.Path(exists=True))
@click.pass_context
def tail(ctx, config_file):
    click.echo('tail')


@cli.command()
@click.argument('config_file', type=click.Path(exists=True))
@click.option('--timeout', type=click.IntRange(min=0, max=3600), default=300,
              help='timeout in seconds')
@click.pass_context
def tail(ctx, config_file, timeout):
    """Tail stack events (stop using CTRL+C) """

    stack_config = load_stack_config(config_file)

    cfn = boto3.resource('cloudformation', region_name=stack_config['Region'])
    stack = cfn.Stack(stack_config['StackName'])

    tail_stack_events(stack, latest_events=0, time_limit=timeout)
