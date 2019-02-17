#  -*- encoding: utf-8 -*-

import os

import click

from ..main import cfn_cli
from ..utils import command_exception_handler
from ...cli import ClickContext
from ...config import ANNOTATED_SAMPLE_CONFIG, SAMPLE_CONFIG


@cfn_cli.command()
@click.option('--annotated', is_flag=True, default=False,
              help='Generate an annotated config')
@click.pass_context
@command_exception_handler
def generate(ctx, annotated):
    """Generate a sample configuration file."""
    assert isinstance(ctx.obj, ClickContext)

    if os.path.exists(ctx.obj.config_filename):
        click.secho('Refuse to overwrite existing file {}'.format(
            ctx.obj.config_filename), fg='red')
    else:
        click.secho('Writing to {}'.format(ctx.obj.config_filename))
        with open(ctx.obj.config_filename, 'w') as fp:
            if annotated:
                fp.write(ANNOTATED_SAMPLE_CONFIG)
            else:
                fp.write(SAMPLE_CONFIG)
