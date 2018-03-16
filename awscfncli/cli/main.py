#  -*- encoding: utf-8 -*-

import os
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
              help='Alternate stack configuration file '
                   '(default: cfn-cli.yml)',
              )
@click.option('--profile',
              type=click.STRING,
              default=None,
              help='Profile name from AWS credential file, overrides '
                   'config/env setting.'
              )
@click.option('--region',
              type=click.STRING,
              default=None,
              help='AWS region to use, overrides config/env setting.'
              )
@click.option('-v', '--verbose', count=True,
              help='Be more verbose.')
def cfn_cli(ctx, file, profile, region, verbose):
    """AWS CloudFormation stack management command line interface.

    By default, cfn-cli try to find "cfn-cli.yml" in
    current directory and load environment and stack configurations.

    Usage:

    \b
      cfn-cli [-f config_file_or_dir] [OPTIONS...] COMMAND SUBCOMMAND [ARGS...] ENVIRONMENT_NAME STACK_NAME
      cfn-cli --help

    Some examples:

    \b
      cfn-cli stack deploy Production Networking
      cfn-cli -f foobar/MyGreatProject.yml stack deploy 'Prod*' 'Net*'

    \b
      cfn-cli stack deploy --help

    """

    ctx_obj = ContextObject(
        config_file=file,
        profile=profile,
        region=region,
        verbosity=verbose,
    )

    if verbose > 1:
        logging.basicConfig(level=logging.DEBUG)

    ctx.obj = ctx_obj
