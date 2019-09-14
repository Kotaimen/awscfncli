"""Dynamic command loader"""

import importlib
import logging
from collections import OrderedDict

import click

logger = logging.getLogger(__name__)

COMMAND_PACKAGE_MAPPING = OrderedDict([
    ("generate", "awscfncli2.cli.commands.generate"),
    ("status", "awscfncli2.cli.commands.status"),
    ("validate", "awscfncli2.cli.commands.validate"),
    ("stack", "awscfncli2.cli.commands.stack"),
    ("drift", "awscfncli2.cli.commands.drift"),
])


class MultiCommand(click.MultiCommand):
    """ Dynamic load commands from packages mapping"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._commands = COMMAND_PACKAGE_MAPPING

    def list_commands(self, ctx):
        return list(self._commands.keys())

    def get_command(self, ctx, cmd_name):
        try:
            pkg_name = self._commands[cmd_name]
        except KeyError:
            logging.error(logger.error(f'Invalid command {cmd_name}'))
            return

        try:
            mod = importlib.import_module(pkg_name)
        except ImportError as e:
            logger.exception(e)
            return

        try:
            return mod.cli
        except AttributeError as e:
            logger.exception(e)
            return
