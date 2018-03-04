#  -*- encoding: utf-8 -*-

import click
import pkg_resources
import boto3

VERSION = pkg_resources.require('awscfncli')[0].version

@click.group()
@click.pass_context
@click.version_option(version=VERSION)
@click.option('-f', '--file',
              type=click.Path(exists=False),
              default='cfn-cli.yml',
              help='Specify an alternate stack configuration file '
                   '(default: cfn-cli.yml)',
              )
# @click.option('--verbose', type=click.,
#               help='Show more output')
def cfn_cli(ctx, file):
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
    # Context object as a dict
    ctx.obj = dict()

    # TODO: Process args

    # TODO: Create boto3 session
    session = boto3.session.Session()
    ctx.obj['session'] = session
