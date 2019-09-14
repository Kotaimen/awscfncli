import os

import click

from awscfncli2.cli.context import Context
from awscfncli2.cli.utils.deco import command_exception_handler
from awscfncli2.config import ANNOTATED_SAMPLE_CONFIG


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
    context = ctx.ensure_object(Context)
    if os.path.exists(context.config_filename):
        click.secho(f'Cowardly refusing overwrite existing {context.config_filename}.',
                    fg='red')
    else:
        click.secho('Writing to {}'.format(context.config_filename))
        with open(context.config_filename, 'w') as fp:
            fp.write(ANNOTATED_SAMPLE_CONFIG)
