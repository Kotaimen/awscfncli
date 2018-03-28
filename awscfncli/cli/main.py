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
                   '(default: cfn-cli.yml)')
@click.option('-t', '--stage',
              type=click.STRING, default='Default',
              help='Specify a deployment stage name or pattern'
                   '(default: Default)')
@click.option('-s', '--stack',
              type=click.STRING, default='*',
              help='Specify a stack name or pattern'
                   '(default: *)')
@click.option('--profile',
              type=click.STRING, default=None,
              help='Profile name from AWS credential file, overrides '
                   'config/env setting.')
@click.option('--region',
              type=click.STRING, default=None,
              help='AWS region to use, overrides config/env setting.')
@click.option('-1', '--one',
              is_flag=True, default=False,
              help='Execute command on first matching ')
@click.option('-v', '--verbose', count=True,
              help='Be more verbose.')
def cfn_cli(ctx, file, stage, stack, profile, region, one, verbose):
    """AWS CloudFormation stack management command line interface.

    Stages and stacks can be selected using globs:

    \b
      cfn-cli --stack=DDB* stack deploy

    Options can be specified using environment variables:

    \b
      CFNCLI_STACK=DDB cfn-cli stack deploy

    Usage:

    \b
      cfn-cli [OPTIONS...] COMMAND SUBCOMMAND [ARGS...]
      cfn-cli --help

    Some examples:

    \b
      cfn-cli stack deploy --help
      cfn-cli -t dev -s ddb stack deploy
      cfn-cli -f foobar/MyGreatProject.yml stack deploy

    """

    ctx_obj = ContextObject(
        config_file=file,
        stage_pattern=stage,
        stack_pattern=stack,
        profile=profile,
        region=region,
        first_stack=one,
        verbosity=verbose,
    )

    if verbose > 1:
        logging.basicConfig(level=logging.DEBUG)

    ctx.obj = ctx_obj
