import click
import yaml

from .colormaps import CHANGESET_STATUS_TO_COLOR, ACTION_TO_COLOR, \
    STACK_STATUS_TO_COLOR
from .events import start_tail_stack_events_daemon


def echo_pair(key, value=None, indent=0,
              value_style=None, key_style=None,
              sep=': '):
    """Pretty print a key value pair
    :param key: The key
    :param value: The value
    :param indent: Number of leading spaces
    :param value_style: click.style parameters of value as a dict, default is none
    :param key_style:  click.style parameters of value as a dict, default is bold text
    :param sep: separator between key and value
    """
    assert key
    key = ' ' * indent + key + sep
    if key_style is None:
        click.secho(key, bold=False, nl=False)
    else:
        click.secho(key, nl=False, **key_style)

    if value is None:
        click.echo('')
    else:

        if value_style is None:
            click.echo(value)
        else:
            click.secho(value, **value_style)


def echo_pair_if_exists(data, key, value, indent=2, key_style=None,
                        value_style=None):
    if value in data:
        echo_pair(key, data[value], indent=indent,
                  key_style=key_style, value_style=value_style, )


class StackPrettyPrinter(object):
    """Pretty print stack parameter, status and events

    Calls click.secho to do the heavy lifting.
    """

    def __init__(self, verbosity=0):
        self.verbosity = verbosity

    def secho(self, text, nl=True, err=False, color=None, **styles):
        click.secho(text, nl=nl, err=err, color=color, **styles)

    def pprint_stack_name(self, qualified_name, stack_name, prefix=None):
        """Print stack qualified name"""
        if prefix:
            click.secho(prefix, bold=True, nl=False)
        click.secho(qualified_name, bold=True)
        echo_pair('StackName', stack_name)

    def pprint_session(self, session, retrieve_identity=True):
        """Print boto3 session"""
        echo_pair('Profile', session.profile_name)
        echo_pair('Region', session.region_name)

        if retrieve_identity:
            sts = session.client('sts')
            identity = sts.get_caller_identity()
            echo_pair('Account', identity['Account'])
            echo_pair('Identity', identity['Arn'])

    def pprint_metadata(self, metadata):
        """Print stack metadata"""
        if self.verbosity > 0:
            click.secho('--- Stack Metadata ---', fg='white', dim=True)
            click.secho(
                yaml.safe_dump(metadata,
                               default_flow_style=False),
                fg='white', dim=True
            )

    def pprint_parameters(self, parameters):
        """Print stack parameters"""
        if self.verbosity > 0:
            click.secho('--- Stack Creation Parameters ---', fg='white', dim=True)
            click.secho(
                yaml.safe_dump(parameters,
                               default_flow_style=False),
                fg='white', dim=True
            )

    def pprint_stack(self, stack):
        """Pretty print stack status"""
        # echo_pair('StackName', stack.stack_name)
        echo_pair('Status', stack.stack_status,
                  value_style=STACK_STATUS_TO_COLOR[stack.stack_status])

        if stack.stack_status == 'STACK_NOT_FOUND':
            return

        echo_pair('StackID', stack.stack_id)
        # echo_pair('Description', stack.description)
        echo_pair('Created', stack.creation_time)
        if stack.last_updated_time:
            echo_pair('Last Updated', stack.last_updated_time)
        echo_pair('Capabilities', stack.capabilities)
        echo_pair('Termination Protection', stack.enable_termination_protection)

    def pprint_stack_parameters(self, stack):

        if stack.parameters:
            echo_pair('Parameters')
            for p in stack.parameters:
                if 'ResolvedValue' in p:
                    # SSM parameter
                    echo_pair(
                        '%s (%s)' % (p['ParameterKey'], p['ParameterValue']),
                        p['ResolvedValue'], indent=2)
                else:
                    echo_pair(p['ParameterKey'], p['ParameterValue'], indent=2)

        if stack.outputs:
            echo_pair('Outputs')
            for o in stack.outputs:
                echo_pair(o['OutputKey'], o['OutputValue'], indent=2)

        if stack.tags:
            echo_pair('Tags')
            for t in stack.tags:
                echo_pair(t['Key'], t['Value'], indent=2)

    def pprint_stack_resources(self, stack):
        echo_pair('Resources')
        for r in stack.resource_summaries.all():
            echo_pair(r.logical_resource_id,
                      '(%s)' % r.resource_type,
                      indent=2, sep=' ')
            echo_pair('Status', r.resource_status,
                      value_style=STACK_STATUS_TO_COLOR[r.resource_status],
                      indent=4)
            echo_pair('Physical ID', r.physical_resource_id, indent=4)
            echo_pair('Last Updated', r.last_updated_timestamp, indent=4)

    def wait_until_deploy_complete(self, session, stack):
        start_tail_stack_events_daemon(session, stack, latest_events=0)

        waiter = session.client('cloudformation').get_waiter(
            'stack_create_complete')
        waiter.wait(StackName=stack.stack_id)

    def wait_until_update_complete(self, session, stack):
        start_tail_stack_events_daemon(session, stack)

        waiter = session.client('cloudformation').get_waiter(
            'stack_update_complete')
        waiter.wait(StackName=stack.stack_id)
