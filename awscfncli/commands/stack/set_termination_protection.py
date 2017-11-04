# -*- encoding: utf-8 -*-

__author__ = 'ray'
__date__ = '05/11/2017'

import click

from ..utils import boto3_exception_handler, pretty_print_config, \
    pretty_print_stack, load_template_body, CANNED_STACK_POLICIES
from ...cli import stack
from ...config import load_stack_config
from .events import start_tail_stack_events_daemon


@stack.command()
@click.argument('config_file', type=click.Path(exists=True))
@click.argument('termination_option', type=click.Choice(['ON', 'OFF']))
@click.pass_context
@boto3_exception_handler
def set_termination_protection(ctx, config_file, termination_option):
    """Update the termination protection...

    \b
    CONFIG_FILE         Stack configuration file.
    TERMINATION_OPTION  Set termination protection to TRUE OR FALSE.
    """
    session = ctx.obj['session']

    # load config
    stack_config = load_stack_config(config_file)
    pretty_print_config(stack_config)

    click.echo('Updating termination protection...')

    # connect co cfn
    region = stack_config.pop('Region')
    client = session.client('cloudformation', region_name=region)
    if termination_option:
        enabled = True if termination_option == 'ON' else False
        try:
            client.update_termination_protection(
                EnableTerminationProtection=enabled,
                StackName=stack_config['StackName']
            )
        except Exception:
            raise NotImplementedError('Termination protection is not supported '
                                      'for current version of boto. '
                                      'Please upgrade to a new version.')

    click.secho('Termination protection is %s.' % termination_option.lower(), fg='green')
