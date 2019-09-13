#  -*- encoding: utf-8 -*-

"""Main cli entry point"""

import logging
import os

import click

from awscfncli2 import __version__
from awscfncli2.cli.context import Context
from awscfncli2.config import DEFAULT_CONFIG_FILE_NAMES
from .multicommand import MultiCommand
from .utils.pprint import StackPrettyPrinter


@click.command(cls=MultiCommand)
@click.version_option(version=__version__)
@click.option('-f', '--file',
              type=click.Path(exists=False, dir_okay=True),
              default=None,
              help='Specify an alternate stack configuration file, default is '
                   'cfn-cli.yml.')
@click.option('-s', '--stack',
              type=click.STRING, default='*',
              help='Select stacks to operate on, defined by STAGE_NAME.STACK_NAME, '
                   'nix glob is supported to select multiple stacks. Default value is '
                   '"*", which means all stacks in all stages.')
@click.option('-p', '--profile',
              type=click.STRING, default=None,
              help='Override AWS profile specified in the config file.  Don\'t use '
                   'this against stacks deploys to multiple profiles.')
@click.option('-r', '--region',
              type=click.STRING, default=None,
              help='Override AWS region specified in the config.  Don\'t use '
                   'this against stacks deploys to multiple regions.')
@click.option('-a', '--artifact-store',
              type=click.STRING, default=None,
              help='Override artifact store specified in the config.  Artifact store is'
                   'the s3 bucket used to store packaged template resource.')
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

    # Set logging level according to verbosity

    if verbose >= 2:
        logging.getLogger().setLevel(logging.DEBUG)
    elif verbose == 1:
        logging.getLogger().setLevel(logging.INFO)
    else:
        logging.getLogger().setLevel(logging.WARNING)

    ppt = StackPrettyPrinter(verbosity=verbose)

    # Find config file
    if file is None:
        # no config file is specified, try default names
        for fn in DEFAULT_CONFIG_FILE_NAMES:
            file = fn
            if os.path.exists(file) and os.path.isfile(file):
                break
    elif os.path.isdir(file):
        # specified a directory, try default names under given dir
        base = file
        for fn in DEFAULT_CONFIG_FILE_NAMES:
            file = os.path.join(base, fn)
            if os.path.exists(file) and os.path.isfile(file):
                break

    # Builds the context object
    ctx_obj = Context(
        config_filename=file,
        stack_selector=stack,
        profile_name=profile,
        region_name=region,
        artifact_store=artifact_store,
        pretty_printer=ppt,
    )

    # Assign context object
    ctx.obj = ctx_obj
