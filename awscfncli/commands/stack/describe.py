# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '11/01/2017'

import boto3
import click

from ..utils import boto3_exception_handler, pretty_print_stack
from ...cli import stack
from ...config import load_stack_config


@stack.command()
@click.argument('config_file', type=click.Path(exists=True))
@click.option('--detail', default=1, type=click.IntRange(min=0,max=2))
@click.pass_context
@boto3_exception_handler
def describe(ctx, config_file, detail):
    """Describe stack status, parmeter and output

    \b
    CONFIG_FILE         Stack configuration file.
    CHANGESET_NAME      The name of the change set.
    """

    stack_config = load_stack_config(config_file)

    cfn = boto3.resource('cloudformation', region_name=stack_config['Region'])
    stack = cfn.Stack(stack_config['StackName'])

    pretty_print_stack(stack, detail=detail)
