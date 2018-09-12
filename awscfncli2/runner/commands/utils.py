import botocore.exceptions

def update_termination_protection(session, parameters, ppt):
    """Update termination protection on a stack"""

    termination_protection = parameters.get('EnableTerminationProtection', None)

    if termination_protection is None:
        # don't care, don't change
        return

    client = session.client('cloudformation')

    if termination_protection:
        ppt.secho('Enabling TerminationProtection')
    else:
        ppt.secho('Disabling TerminationProtection', fg='red')

    client.update_termination_protection(
        StackName=parameters['StackName'],
        EnableTerminationProtection=termination_protection)


def is_stack_does_not_exist_exception(ex):
    """Check whether given exception is "stack does not exist",
    botocore doesn't throw a distinct exception class in this case
    """
    if isinstance(ex, botocore.exceptions.ClientError):
        error = ex.response.get('Error', {})
        error_message = error.get('Message', 'Unknown')
        return error_message.endswith('does not exist')
    else:
        return False