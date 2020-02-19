"""Main click command."""

import logging

import click

from awscfncli2 import __version__
from .autocomplete import stack_auto_complete, profile_auto_complete, install_callback
from .context import Context, Options, DefaultContextBuilder
from .multicommand import MultiCommand

CONTEXT_BUILDER = DefaultContextBuilder
VERBOSITY_LOGLEVEL_MAPPING = [logging.WARNING, logging.INFO, logging.DEBUG]

import click_completion
# XXX: Monkey patch dynamic completion
from . monkeypatch_clickcompletion import monkey_patch
monkey_patch()
click_completion.init()


@click.command(cls=MultiCommand)
@click.version_option(version=__version__)
@click.option('--install-completion', is_flag=True, callback=install_callback,
              expose_value=False,
              help='Automatically install completion for the current shell. Make sure '
                   'to have psutil installed.')
@click.option('-f', '--file',
              type=click.Path(exists=False, dir_okay=True),
              default=None,
              help='Specify an alternate stack configuration file, default is '
                   'cfn-cli.yml.')
@click.option('-s', '--stack', autocompletion=stack_auto_complete,
              type=click.STRING, default='*',
              help='Select stacks to operate on, defined by STAGE_NAME.STACK_NAME, '
                   'nix glob is supported to select multiple stacks. Default value is '
                   '"*", which means all stacks in all stages.')
@click.option('-p', '--profile', autocompletion=profile_auto_complete,
              type=click.STRING, default=None,
              help='Override AWS profile specified in the config file.  Warning: '
                   'Don\'t use this option on stacks in different accounts.')
@click.option('-r', '--region',
              type=click.STRING, default=None,
              help='Override AWS region specified in the config.  Warning: Don\'t use '
                   'this option on stacks in different regions.')
@click.option('-a', '--artifact-store',
              type=click.STRING, default='',
              help='Override artifact store specified in the config.  Artifact store is'
                   'the s3 bucket used to store packaged template resource.  Warning: '
                   'Don\'t use this option on stacks in different accounts & regions.')
@click.option('-v', '--verbose', count=True,
              help='Be more verbose, can be specified multiple times.')
@click.pass_context
def cli(ctx, file, stack, profile, region, artifact_store, verbose):
    """AWS CloudFormation CLI - The missing CLI for CloudFormation.

    Quickstart: use `cfn-cli generate` to generate a new project.

    cfn-cli operates on a single YAML based config file and can manages stacks
    across regions & accounts.  By default, cfn-cli will try to locate config file
    cfn-cli.yml in current directory, override this using -f option:

    \b
        cfn-cli -f some-other-config-file.yaml <command>

    If the config contains multiple stacks, they can be can be selected using
    full qualified stack name:

    \b
        cfn-cli -s StageName.StackName <command>

    Unix style globs is also supported when selecting stacks to operate on:
    \b
        cfn-cli -s Backend.* <command>

    By default, command operates on all stacks in every stages, with order specified
    in the config file.

    Options can also be specified using environment variables:

    \b
        CFN_STACK=StageName.StackName cfn-cli <command>
    """

    # Setup global logging level
    if verbose >= 2: verbose = 2  # cap at 2

    logger = logging.getLogger()
    logger.setLevel(VERBOSITY_LOGLEVEL_MAPPING[verbose])

    # Build context from command options
    options = Options(
        config_filename=file,
        stack_selector=stack,
        profile_name=profile,
        region_name=region,
        artifact_store=artifact_store,
        verbosity=verbose,
    )
    context: Context = CONTEXT_BUILDER(options).build()

    # Assign context object
    ctx.obj = context
