import traceback
from functools import wraps

import botocore.exceptions
import click

from awscfncli2.config import ConfigError


def command_exception_handler(f):
    """Capture and pretty print exceptions."""

    @wraps(f)
    def wrapper(ctx, *args, **kwargs):
        try:
            return f(ctx, *args, **kwargs)
        except (botocore.exceptions.ClientError,
                botocore.exceptions.BotoCoreError,
                ) as e:
            if ctx.obj.verbosity > 0:
                click.secho(traceback.format_exc(), fg='red')
            else:
                click.secho(str(e), fg='red')
            raise click.Abort
        except ConfigError as e:
            click.secho(str(e), fg='red')
            if ctx.obj.verbosity > 0:
                traceback.print_exc()
            raise click.Abort

    return wrapper
