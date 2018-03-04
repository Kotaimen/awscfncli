#  -*- encoding: utf-8 -*-

import click
from ..main import cfn_cli

@cfn_cli.group()
@click.pass_context
def stack(ctx):
    """Commands operate on CloudFormation stacks"""
    pass

