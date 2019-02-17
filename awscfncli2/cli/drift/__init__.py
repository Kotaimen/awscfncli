import click
from ..main import cfn_cli
from ...config import ConfigError

@cfn_cli.group()
@click.pass_context
def drift(ctx):
    """Drift detection."""
    pass
