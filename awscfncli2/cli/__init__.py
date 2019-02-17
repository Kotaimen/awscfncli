# Import all commands here so they get registered in Click
from .main import cfn_cli

from .context import ClickContext

from .commands.status import status
from .commands.validate import validate
from .commands.generate import generate

from .stack.sync import sync
from .stack.describe import describe
from .stack.deploy import deploy
from .stack.delete import delete
from .stack.update import update
from .stack.tail import tail
from .stack.cancel import cancel

from .drift.detect import detect
from .drift.diff import diff
