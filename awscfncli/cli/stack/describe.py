#  -*- encoding: utf-8 -*-

import click
from . import stack

@stack.command()
@click.pass_context
def describe(ctx):
    """Print status, parameters, outputs, stack resources and export values
    of the stack specified in the configuration file."""
    print('stack.describe')
