# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '21/07/2017'

import click

from ...config import load_stack_config
from ...cli import template
from ..utils import boto3_exception_handler, load_template_body


@template.command()
@click.argument('config_file', type=click.Path(exists=True))
@click.argument('packaged_template', type=click.Path(exists=False))
@click.pass_context
@boto3_exception_handler
def package(ctx, config_file, packaged_template):
    """Package template specified in the stack configuration file.

    \b
    CONFIG_FILE         Stack configuration file.
    OUTPUT_TEMPLATE     Name of the output template
    """
    session = ctx.obj['session']

    click.echo('Packing template...')
    stack_config = load_stack_config(config_file)

    load_template_body(session, stack_config)

    with open(packaged_template, 'w') as fp:
        # Content of the packaged template has been wrote into the TemplateBody
        # while loading.
        fp.write(stack_config['TemplateBody'])

    click.echo('Template packaging complete.')
