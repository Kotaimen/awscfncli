#  -*- encoding: utf-8 -*-

import click
from ..main import cfn_cli
from ...config import ConfigError

@cfn_cli.group()
@click.pass_context
def changeset(ctx):
    """Commands operate on CloudFormation stack changesets"""
    try:
        ctx.obj.load()
    except ConfigError as e:
        click.secho(str(e), fg='red')
        raise SystemExit

