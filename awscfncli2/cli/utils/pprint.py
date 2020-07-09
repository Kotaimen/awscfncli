"""Proxy interfaces for cli print."""
import difflib
import json

import backoff
import botocore.exceptions
import click
import yaml

from .colormaps import CHANGESET_STATUS_TO_COLOR, CHANGESET_ACTION_TO_COLOR, \
    CHANGESET_REPLACEMENT_TO_COLOR, DRIFT_STATUS_TO_COLOR, \
    STACK_STATUS_TO_COLOR, CHANGESET_RESOURCE_REPLACEMENT_TO_COLOR
from .common import is_rate_limited_exception, is_not_rate_limited_exception
from .events import start_tail_stack_events_daemon
from .pager import custom_paginator


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

    def echo_pair(self, key, value=None, indent=0,
                  value_style=None, key_style=None,
                  sep=': '):
        echo_pair(key, value=value, indent=indent, value_style=value_style,
                  key_style=key_style, sep=sep)

    def confirm(self, *args, **argv):
        return click.confirm(*args, **argv)

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
            for k, v in metadata.items():
                echo_pair(k, repr(v),
                          key_style={'fg': 'white', 'dim': True},
                          value_style={'fg': 'white', 'dim': True}
                          )

    def pprint_parameters(self, parameters):
        """Print stack parameters"""
        if self.verbosity > 0:
            click.secho('--- Stack Creation Parameters ---', fg='white',
                        dim=True)
            for k, v in parameters.items():
                if k not in ('TemplateBody', 'StackPolicyBody'):
                    echo_pair(k, repr(v),
                              key_style={'fg': 'white', 'dim': True},
                              value_style={'fg': 'white', 'dim': True}
                              )
                else:
                    click.secho('--- start of {} ---'.format(k), fg='white',
                                dim=True)
                    click.secho(v, fg='white', dim=True)
                    click.secho('--- end of {} ---'.format(k), fg='white',
                                dim=True)

    def pprint_stack(self, stack, status=False):
        """Pretty print stack status"""
        # echo_pair('StackName', stack.stack_name)
        if status:
            echo_pair('Status', stack.stack_status,
                      value_style=STACK_STATUS_TO_COLOR[stack.stack_status])

        if stack.stack_status == 'STACK_NOT_FOUND':
            return

        echo_pair('StackID', stack.stack_id)
        # echo_pair('Description', stack.description)
        echo_pair('Created', stack.creation_time)
        if stack.last_updated_time:
            echo_pair('Last Updated', stack.last_updated_time)
        if stack.capabilities:
            echo_pair('Capabilities', ', '.join(stack.capabilities),
                      value_style={'fg': 'yellow'})
        echo_pair('TerminationProtection',
                  str(stack.enable_termination_protection),
                  value_style={
                      'fg': 'red'} if stack.enable_termination_protection else None
                  )

        drift_status = stack.drift_information['StackDriftStatus']
        drift_timestamp = stack.drift_information.get('LastCheckTimestamp')
        echo_pair('Drift Status', drift_status,
                  value_style=DRIFT_STATUS_TO_COLOR[drift_status])
        if drift_timestamp:
            echo_pair('Lasted Checked', drift_timestamp)

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

        for res in stack.resource_summaries.all():

            logical_id = res.logical_resource_id
            physical_id = res.physical_resource_id
            res_type = res.resource_type
            status = res.resource_status
            status_reason = res.resource_status_reason
            drift_status = res.drift_information.get('StackResourceDriftStatus')
            drift_timestamp = res.drift_information.get('LastCheckTimestamp',
                                                        None)
            last_updated = res.last_updated_timestamp

            echo_pair('{} ({})'.format(logical_id, res_type), indent=2)
            echo_pair('Physical ID', physical_id, indent=4)
            echo_pair('Last Updated', last_updated, indent=4)
            echo_pair('Status', status,
                      value_style=STACK_STATUS_TO_COLOR[status],
                      indent=4)
            if status_reason:
                echo_pair('Reason', status_reason, indent=6)
            echo_pair('Drift Status', drift_status,
                      value_style=DRIFT_STATUS_TO_COLOR[drift_status], indent=4)
            if drift_timestamp:
                echo_pair('Lasted Checked', drift_timestamp, indent=6)

    def pprint_stack_exports(self, stack, session):
        client = session.client('cloudformation')
        echo_pair('Exports')
        for export in custom_paginator(client.list_exports, 'Exports'):
            if export['ExportingStackId'] == stack.stack_id:
                echo_pair(export['Name'], export['Value'], indent=2)
                try:
                    for import_ in custom_paginator(client.list_imports,
                                                    'Imports',
                                                    ExportName=export[
                                                        'Name']):
                        echo_pair('Imported By', import_, indent=4)
                except botocore.exceptions.ClientError as e:
                    pass

    def pprint_changeset(self, result):

        status = result['Status']
        status_reason = result.get('StatusReason', None)

        echo_pair('ChangeSet Status', status,
                  value_style=CHANGESET_STATUS_TO_COLOR[status])
        if status_reason:
            echo_pair('Status Reason', status_reason)

        echo_pair('Resource Changes')
        for change in result['Changes']:
            logical_id = change['ResourceChange']['LogicalResourceId']
            res_type = change['ResourceChange']['ResourceType']
            action = change['ResourceChange']['Action']
            replacement = change['ResourceChange'].get('Replacement', None)
            change_res_id = change['ResourceChange'].get('PhysicalResourceId',
                                                         None)
            change_scope = change['ResourceChange'].get('Scope', None)
            change_details = {}
            for detail in change['ResourceChange'].get('Details', None):
                if detail['Target'].get('Name', None):
                    if detail['Target']['Name'] not in change_details or detail[
                        'Evaluation'] == 'Static':
                        change_details[detail['Target']['Name']] = detail

            echo_pair('{} ({})'.format(logical_id, res_type), indent=2)
            echo_pair('Action', action,
                      value_style=CHANGESET_ACTION_TO_COLOR[action], indent=4)
            if replacement:
                echo_pair('Replacement', replacement,
                          value_style=CHANGESET_REPLACEMENT_TO_COLOR[
                              replacement],
                          indent=4)
            if change_res_id:
                echo_pair('Physical Resource', change_res_id, indent=4)
            if change_scope:
                echo_pair('Change Scope', ','.join(change_scope), indent=4)
            if len(change_details):
                echo_pair('Changed Properties', '', indent=4)
                for k, v in change_details.items():
                    echo_pair(k, indent=6)
                    echo_pair('Requires Recreation',
                              v['Target']['RequiresRecreation'],
                              value_style=
                              CHANGESET_RESOURCE_REPLACEMENT_TO_COLOR[
                                  v['Target']['RequiresRecreation']], indent=8)
                    if v.get('CausingEntity', None):
                        echo_pair('Causing Entity', v['CausingEntity'],
                                  indent=8)
                    self.pair = echo_pair('Change Source', v['ChangeSource'],
                                          indent=8)

    def pprint_stack_drift(self, drift):
        detection_status = drift['DetectionStatus']
        drift_status = drift['StackDriftStatus']
        drifted_resources = drift['DriftedStackResourceCount']
        timestamp = drift['Timestamp']

        echo_pair('Drift Detection Status',
                  detection_status,
                  value_style=DRIFT_STATUS_TO_COLOR[detection_status])
        echo_pair('Stack Drift Status',
                  drift_status,
                  value_style=DRIFT_STATUS_TO_COLOR[drift_status])
        echo_pair('Drifted resources',
                  drifted_resources)
        echo_pair('Timestamp', timestamp)

    def pprint_resource_drift(self, status):
        logical_id = status['LogicalResourceId']
        res_type = status['ResourceType']
        physical_id = status['PhysicalResourceId']
        physical_resource_context = status.get('PhysicalResourceIdContext', [])
        drift_status = status['StackResourceDriftStatus']
        timestamp = status['Timestamp']

        echo_pair('{} ({})'.format(logical_id, res_type), indent=2)
        echo_pair('Physical Id', physical_id, indent=4)
        for context in physical_resource_context:
            echo_pair(context['Key'], context['Value'], indent=4)
        echo_pair('Drift Status', drift_status,
                  value_style=DRIFT_STATUS_TO_COLOR[drift_status], indent=4)
        echo_pair('Timestamp', timestamp, indent=4)

        if 'ExpectedProperties' not in status:
            return

        echo_pair('Property Diff', '>', indent=4)
        expected = yaml.safe_dump(
            json.loads(status['ExpectedProperties']),
            default_flow_style=False)

        actual = yaml.safe_dump(
            json.loads(status['ActualProperties']),
            default_flow_style=False)
        diff = difflib.unified_diff(
            expected.splitlines(), actual.splitlines(),
            'Expected', 'Actual', n=5)

        for n, line in enumerate(diff):
            # skip file names and diff stat
            if n < 5: continue
            if line.startswith('-'):
                click.secho('      ' + line, fg='red')
            elif line.startswith('+'):
                click.secho('      ' + line, fg='green')
            else:
                click.secho('      ' + line)

    @backoff.on_exception(backoff.expo, botocore.exceptions.WaiterError, max_tries=10,
                          giveup=is_not_rate_limited_exception)
    def wait_until_deploy_complete(self, session, stack, disable_tail_events=False):
        if not disable_tail_events:
            start_tail_stack_events_daemon(session, stack, latest_events=0)

        waiter = session.client('cloudformation').get_waiter(
            'stack_create_complete')
        waiter.wait(StackName=stack.stack_id)

    @backoff.on_exception(backoff.expo, botocore.exceptions.WaiterError, max_tries=10,
                          giveup=is_not_rate_limited_exception)
    def wait_until_delete_complete(self, session, stack):
        start_tail_stack_events_daemon(session, stack)

        waiter = session.client('cloudformation').get_waiter(
            'stack_delete_complete')
        waiter.wait(StackName=stack.stack_id)

    @backoff.on_exception(backoff.expo, botocore.exceptions.WaiterError, max_tries=10,
                          giveup=is_not_rate_limited_exception)
    def wait_until_update_complete(self, session, stack, disable_tail_events=False):
        if not disable_tail_events:
            start_tail_stack_events_daemon(session, stack)

        waiter = session.client('cloudformation').get_waiter(
            'stack_update_complete')
        waiter.wait(StackName=stack.stack_id)

    @backoff.on_exception(backoff.expo, botocore.exceptions.WaiterError, max_tries=10,
                          giveup=is_not_rate_limited_exception)
    def wait_until_changset_complete(self, client, changeset_id):
        waiter = client.get_waiter('change_set_create_complete')
        try:
            waiter.wait(ChangeSetName=changeset_id)
        except botocore.exceptions.WaiterError as e:
            if is_rate_limited_exception(e):
                # change set might be created successfully but we got throttling error, retry is needed so rerasing exception
                raise
            click.secho('ChangeSet create failed.', fg='red')
        else:
            click.secho('ChangeSet create complete.', fg='green')
