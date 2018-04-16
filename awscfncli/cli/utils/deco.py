from functools import wraps

import botocore.exceptions
import click

from ...config import ConfigError

def boto3_exception_handler(f):
    """Capture and pretty print exceptions"""

    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except (botocore.exceptions.ClientError,
                botocore.exceptions.WaiterError,
                botocore.exceptions.ValidationError,
                botocore.exceptions.ParamValidationError,
                ) as e:
            click.secho(str(e), fg='red')
            raise click.Abort
        except ConfigError as e:
            click.secho(str(e), fg='red')
            raise click.Abort

    return wrapper
