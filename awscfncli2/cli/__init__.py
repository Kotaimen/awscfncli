# Import all commands here so they get registered in Click
from .main import cfn_cli

from .commands.status import status
from .commands.validate import validate

from .stack.sync import sync
from .stack.describe import describe
from .stack.deploy import deploy
from .stack.delete import delete
from .stack.update import update
from .stack.tail import tail
