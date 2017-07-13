# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '11/01/2017'

import click

from ...config import load_stack_config
from ...cli import template
from ..utils import boto3_exception_handler, load_template_body


@template.command()
@click.argument('config_file', type=click.Path(exists=True))
@click.pass_context
@boto3_exception_handler
def validate(ctx, config_file):
    """Validate template specified in the stack configuration file.

    AWS CloudFormation first checks if the template is valid JSON. If it isn't,
    AWS CloudFormation checks if the template is valid YAML. If both these
    checks fail, AWS CloudFormation returns a template validation error.

    CONFIG_FILE         Stack configuration file.
    """
    session = ctx.obj['session']

    click.echo('Validating template...')
    stack_config = load_stack_config(config_file)
    load_template_body(session, stack_config)

    client = session.client('cloudformation')

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
