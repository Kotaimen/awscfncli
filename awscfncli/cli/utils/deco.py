from functools import wraps

import botocore.exceptions
import click

def boto3_exception_handler(f):
    """Capture and pretty print exceptions"""

    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except (botocore.exceptions.ClientError,
                botocore.exceptions.WaiterError,
                botocore.exceptions.ParamValidationError,
                ) as e:
            click.secho(str(e), fg='red')
        except RuntimeError as e:
            click.secho(str(e), fg='red')
        except KeyboardInterrupt as e:
            click.secho('Aborted.', fg='red')

    return wrapper
