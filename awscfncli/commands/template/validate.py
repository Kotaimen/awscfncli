# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '11/01/2017'

import boto3
import click

from ...config import load_stack_config
from ...cli import template
from ..utils import boto3_exception_handler


@template.command()
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
