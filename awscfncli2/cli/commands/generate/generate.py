import os

import click

from awscfncli2.cli.context import Context
from awscfncli2.cli.utils.deco import command_exception_handler
from awscfncli2.config import ANNOTATED_SAMPLE_CONFIG


@click.command('generate')
@click.option('--annotated',
              expose_value=False,
              hidden=True,
              is_flag=True,
              default=True,
              help='Generate an annotated config, this option is deprecated and will '
                   'be removed from future versions.')
@click.pass_context
@command_exception_handler
def cli(ctx):
    """Generate a sample configuration file to cfn-cli.yaml."""
    context = ctx.ensure_object(Context)
    if os.path.exists(context.config_filename):
        click.secho(f'Refuse to overwrite existing file {context.config_filename}',
                    fg='red')
    else:
        click.secho('Writing to {}'.format(context.config_filename))
        with open(context.config_filename, 'w') as fp:
            fp.write(ANNOTATED_SAMPLE_CONFIG)
