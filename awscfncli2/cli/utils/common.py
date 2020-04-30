import botocore.exceptions


def is_rate_limited_exception(e):
    if isinstance(e, (botocore.exceptions.ClientError, botocore.exceptions.WaiterError)):
        return 'Rate exceeded' in str(e)
    else:
        return False


def is_not_rate_limited_exception(e):
    return not is_rate_limited_exception(e)
