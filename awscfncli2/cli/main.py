#  -*- encoding: utf-8 -*-

"""Main cli entrypoint"""

import logging
import os
import click
import pkg_resources

from .context import ClickContext
from .utils import StackPrettyPrinter

VERSION = pkg_resources.require('awscfncli2')[0].version

DEFAULT_CONFIG_FILE_NAMES = ['cfn-cli.yaml', 'cfn-cli.yml']


@click.group()
@click.pass_context
@click.version_option(version=VERSION)
@click.option('-f', '--file',
              type=click.Path(exists=False, dir_okay=True),
              default=None,
              help='Specify an alternate stack configuration file '
                   '(default: cfn-cli.yml).')
@click.option('-s', '--stack',
              type=click.STRING, default='*',
              help='Stack selector, specify stacks to operate on, defined by '
                   'STAGE_NAME.STACK_NAME (default value is "*", which means '
                   'all stacks in all stages).')
@click.option('-p', '--profile',
              type=click.STRING, default=None,
              help='Override AWS profile specified in the config.')
@click.option('-r', '--region',
              type=click.STRING, default=None,
              help='Override AWS region specified in the config.')
@click.option('-a', '--artifact-store',
              type=click.STRING, default=None,
              help='Override ArtifactStore (AWS bucket name) specified in the config.')
@click.option('-v', '--verbose', count=True,
              help='Be more verbose, can be specified multiple times.')
def cfn_cli(ctx, file, stack, profile, region, artifact_store, verbose):
    """AWS CloudFormation stack management command line interface.

    Options can also be specified using environment variables:

    \b
        CFN_STACK=Default.DDB1 cfn-cli deploy
    
    By default, cfn-cli will try to locate cfn-cli.yml file in 
    current directory, override this using -f option.

    Stack can be selected using full qualified name:
    
    \b
        cfn-cli -s Default.DDB1 describe
    
    Default is the stage name and DDB1 is stack name, unix globs is also 
    supported when selecting stacks to operate on:
    
    \b
        cfn-cli -s Default.DDB* describe
        cfn-cli -s Def*.DDB1 describe

    If "." is missing from stack selector, "cfn-cli" will assume
    stage name "*" is specified, thus "*" is equivalent to "*.*", which
    means all stacks in all stages.
    """

    # Set logging level according to verbosity
    if verbose == 2:
        logging.getLogger().setLevel(logging.DEBUG)
    elif verbose == 1:
        logging.getLogger().setLevel(logging.INFO)
    else:
        logging.getLogger().setLevel(logging.WARNING)

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
    ctx_obj = ClickContext(
        config_filename=file,
        stack_selector=stack,
        profile_name=profile,
        region_name=region,
        artifact_store = artifact_store,
        pretty_printer=StackPrettyPrinter(verbosity=verbose),

    )

    # Assign context object
    ctx.obj = ctx_obj
