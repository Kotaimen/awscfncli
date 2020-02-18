import os

import click

from awscfncli2.cli.context import Context
from awscfncli2.cli.utils.deco import command_exception_handler
from awscfncli2.config import ANNOTATED_SAMPLE_CONFIG, DEFAULT_CONFIG_FILE_NAMES


@click.command('generate')
# TODO: Deprecate this
@click.option('--annotated',
              expose_value=False,
              hidden=True,
              is_flag=True,
              default=True,
              help='This option is deprecated and will be removed in future versions.')
@click.pass_context
@command_exception_handler
def cli(ctx):
    """Generate sample configuration file.

    Generate a annotated configuration file as `cfn-cli.yaml` in working directory.
    """
    filename = DEFAULT_CONFIG_FILE_NAMES[0]
    if os.path.exists(filename):
        click.secho(f'Cowardly refusing overwrite existing {filename}.',
                    fg='red')
    else:
        click.secho(f'Writing to {filename}')
        with open(filename, 'w') as fp:
            fp.write(ANNOTATED_SAMPLE_CONFIG)
