import botocore.exceptions


def update_termination_protection(session,
                                  termination_protection,
                                  stack_name,
                                  ppt):
    """Update termination protection on a stack"""

    if termination_protection is None:
        # don't care, don't change
        return

    client = session.client('cloudformation')

    if termination_protection:
        ppt.secho('Enabling TerminationProtection')
    else:
        ppt.secho('Disabling TerminationProtection', fg='red')

    client.update_termination_protection(
        StackName=stack_name,
        EnableTerminationProtection=termination_protection)


def is_stack_does_not_exist_exception(ex):
    """Check whether given exception is "stack does not exist",
    botocore doesn't throw a distinct exception class in this case.
    """
    if isinstance(ex, botocore.exceptions.ClientError):
        error = ex.response.get('Error', {})
        error_message = error.get('Message', 'Unknown')
        return error_message.endswith('does not exist')
    else:
        return False


def is_no_updates_being_performed_exception(ex):
    """Check whether given exception is "no update to be performed"
    botocore doesn't throw a distinct exception class in this case.
    """
    if isinstance(ex, botocore.exceptions.ClientError):
        error = ex.response.get('Error', {})
        error_message = error.get('Message', 'Unknown')
        return error_message.endswith('No updates are to be performed.')
    else:
        return False


def is_stack_already_exists_exception(ex):
    """Check whether given exception is "stack already exist"
    Exception class is dynamiclly generated in botocore.
    """
    return ex.__class__.__name__ == 'AlreadyExistsException'
