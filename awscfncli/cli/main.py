#  -*- encoding: utf-8 -*-

"""Main cli entrypoint"""

import logging

import click
import pkg_resources

from .utils.context import ContextObject

VERSION = pkg_resources.require('awscfncli')[0].version


@click.group()
@click.pass_context
@click.version_option(version=VERSION)
@click.option('-f', '--file',
              type=click.Path(exists=False, dir_okay=True),
              default='cfn-cli.yml',
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
@click.option('-1', '--one',
              is_flag=True, default=False,
              help='Select only the first matching stack if glob is used '
                   'in --stack option.')
@click.option('-v', '--verbose', count=True,
              help='Be more verbose.')
def cfn_cli(ctx, file, stack, profile, region, one, verbose):
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
    stage name "*" is specfied, thus "*" is equivalent to "*.*", which
    means all stacks in all stages.
    """

    # Builds the context object which contains config object and stack
    # selection query parsers.
    ctx_obj = ContextObject(
        config_file=file,
        stack_selector=stack,
        profile=profile,
        region=region,
        first_stack=one,
        verbosity=verbose,
    )

    if verbose > 0:
        logging.basicConfig(level=logging.DEBUG)

    ctx.obj = ctx_obj
