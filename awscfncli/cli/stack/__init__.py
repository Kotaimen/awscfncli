#  -*- encoding: utf-8 -*-

import click
from ..main import cfn_cli
from ...config import ConfigError

@cfn_cli.group()
@click.pass_context
def stack(ctx):
    """Commands operate on CloudFormation stacks"""
    try:
        ctx.obj.stacks
    except ConfigError as e:
        click.secho(str(e), fg='red')
        raise SystemExit

