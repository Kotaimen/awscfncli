#  -*- encoding: utf-8 -*-

import click
import pkg_resources
import boto3
import collections

from ..config import load_config

VERSION = pkg_resources.require('awscfncli')[0].version


class ContextObject(
    collections.namedtuple('CfnCliContext',
                           'session profile region config verbosity')):
    pass


@click.group()
@click.pass_context
@click.version_option(version=VERSION)
@click.option('-f', '--file',
              type=click.Path(exists=False),
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

    Typical usage:

    \b
      cfn-cli [OPTIONS] COMMAND SUBCOMMAND [ARGS...] ENVIRONMENT_NAME STACK_NAME

    For example:

    \b
      cfn-cli stack deploy Production Networking

    To retrieve help, use '--help':

    \b
      cfn-cli stack deploy --help

    """

    session = boto3.session.Session(
        profile_name=profile,
        region_name=region,
    )

    config = load_config(file)

    ctx_obj = ContextObject(
        session=session,
        profile=profile,
        region=region,
        verbosity=verbose,
        config=config
    )

    ctx.obj = ctx_obj
