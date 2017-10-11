# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '8/23/17'

import click

from ...config import load_stack_config
from ...cli import template
from ..utils import boto3_exception_handler, load_template_body

@template.command()
@click.argument('config_file', type=click.Path(exists=True))
@click.pass_context
@boto3_exception_handler
def costs(ctx, config_file):
    """Estimate cost of the stack.

    \b
    CONFIG_FILE         Stack configuration file.
    """
    session = ctx.obj['session']

    click.echo('Packing template...')
    stack_config = load_stack_config(config_file)

    load_template_body(session, stack_config)

    # connect to cfn
    region = stack_config.pop('Region')
    client = session.client('cloudformation', region_name=region)

    parameters = dict()
    parameter_keys = ['TemplateBody', 'TemplateURL', 'Parameters']
    for key in parameter_keys:
        if key in stack_config:
            parameters[key] = stack_config.get(key)

    cost_estimate = client.estimate_template_cost(**parameters)

    click.echo('Cost Estimate Url: %s' % cost_estimate['Url'])

