import click
import yaml


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


def echo_pair_if_exists(data, key, value, indent=2, key_style=None, value_style=None):
    if value in data:
        echo_pair(key, data[value], indent=indent,
                  key_style=key_style, value_style=value_style, )


def pretty_print_config(qualified_name, stack_config, session, verbosity=0,
                        retrieve_identity=False):
    """Pretty stack config"""
    click.secho(qualified_name, bold=True)

    echo_pair('Profile', session.profile_name)
    echo_pair('Region', session.region_name)

    # following requires dry run
    if retrieve_identity:
        sts = session.client('sts')
        identity = sts.get_caller_identity()
        echo_pair('Account', identity['Account'])
        echo_pair('Identity', identity['Arn'])

    if verbosity > 0:
        click.secho(
            yaml.safe_dump(stack_config, default_flow_style=False),
            fg='white', dim=True
        )

    echo_pair('Stack Name', stack_config['StackName'])


def pretty_print_stack(stack, detail=False):
    """Pretty print stack status"""
    echo_pair('Stack ID', stack.stack_id)

    if not detail:
        return

    # echo_pair('Name', stack.stack_name)
    echo_pair('Description', stack.description)

    echo_pair('Status', stack.stack_status,
              value_style=STACK_STATUS_TO_COLOR[stack.stack_status])
    echo_pair('Created', stack.creation_time)
    if stack.last_updated_time:
        echo_pair('Last Updated', stack.last_updated_time)
    echo_pair('Capabilities', stack.capabilities)
    echo_pair('Termination Protection', stack.enable_termination_protection)

    if stack.parameters:
        echo_pair('Parameters')
        for p in stack.parameters:
            if 'ResolvedValue' in p:
                # SSM parameter
                echo_pair('%s (%s)' % (p['ParameterKey'], p['ParameterValue']),
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


#
# Status string to click.style mapping
#
STACK_STATUS_TO_COLOR = {
    'CREATE_IN_PROGRESS': dict(fg='yellow'),
    'CREATE_FAILED': dict(fg='red'),
    'CREATE_COMPLETE': dict(fg='green'),
    'ROLLBACK_IN_PROGRESS': dict(fg='yellow'),
    'ROLLBACK_FAILED': dict(fg='red'),
    'ROLLBACK_COMPLETE': dict(fg='red'),
    'DELETE_IN_PROGRESS': dict(fg='yellow'),
    'DELETE_FAILED': dict(fg='red'),
    'DELETE_SKIPPED': dict(fg='white', dim=True),
    'DELETE_COMPLETE': dict(fg='white', dim=True),
    'UPDATE_IN_PROGRESS': dict(fg='yellow'),
    'UPDATE_COMPLETE_CLEANUP_IN_PROGRESS': dict(fg='green'),
    'UPDATE_COMPLETE': dict(fg='green'),
    'UPDATE_ROLLBACK_IN_PROGRESS': dict(fg='red'),
    'UPDATE_ROLLBACK_FAILED': dict(fg='red'),
    'UPDATE_ROLLBACK_COMPLETE_CLEANUP_IN_PROGRESS': dict(fg='red'),
    'UPDATE_ROLLBACK_COMPLETE': dict(fg='green'),
    'UPDATE_FAILED': dict(fg='red'),
    'REVIEW_IN_PROGRESS': dict(fg='yellow'),
    # custom status:
    'STACK_NOT_FOUND': dict(fg='red')
}

CHANGESET_STATUS_TO_COLOR = {
    'UNAVAILABLE': dict(fg='white', dim=True),
    'AVAILABLE': dict(fg='green'),
    'EXECUTE_IN_PROGRESS': dict(fg='yellow'),
    'EXECUTE_COMPLETE': dict(fg='green'),
    'EXECUTE_FAILED': dict(fg='red'),
    'OBSOLETE': dict(fg='white', dim=True),

    'CREATE_PENDING': dict(fg='white', dim=True),
    'CREATE_IN_PROGRESS': dict(fg='yellow'),
    'CREATE_COMPLETE': dict(fg='green'),
    'DELETE_COMPLETE': dict(fg='white', dim=True),
    'FAILED': dict(fg='red'),
}

ACTION_TO_COLOR = {
    'Add': dict(fg='green'),
    'Modify': dict(fg='yellow', dim=True),
    'Remove': dict(fg='red'),
}
