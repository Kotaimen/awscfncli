import logging
import time
import traceback
from functools import wraps

import botocore.exceptions
import click

from awscfncli2.config import ConfigError

logger = logging.getLogger(__name__)


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


def retry_on_throttling(tries=4, delay=2, backoff=2):
    """
    Retries function on Throttling errors raised by WaiterError or ClientError

    Args:
        tries: number of attempts before raising any exceptions
        delay: initial delay between retries in seconds
        backoff: backoff multiplier e.g. value of 2 will double the delay each retry
    """

    def decorator_retry(f):
        @wraps(f)
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                except (botocore.exceptions.WaiterError, botocore.exceptions.ClientError) as e:
                    if 'Rate exceeded' in str(e):
                        logger.warning(f"{str(e)}, Retrying in {mdelay} seconds...")
                        time.sleep(mdelay)
                        mtries -= 1
                        mdelay *= backoff
                    else:
                        raise
            return f(*args, **kwargs)

        return f_retry

    return decorator_retry
