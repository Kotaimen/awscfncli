#  -*- encoding: utf-8 -*-

import click
from . import stack

@stack.command()
@click.pass_context
def deploy(ctx):
    """Deploy a new stack using specified configuration."""
    print('stack.deploy')
