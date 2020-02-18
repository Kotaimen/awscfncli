import os
from unittest.mock import patch
import click.testing

from awscfncli2.cli.main import cli
from awscfncli2.cli.context import Context


def test_main():

    cli_runner = click.testing.CliRunner()

    with cli_runner.isolated_filesystem():
        # by default, print help when invoked with no options
        result = cli_runner.invoke(cli)
        assert result.exit_code == 0
        assert "AWS CloudFormation CLI" in result.output
        # Generate a sample config
        cli_runner.invoke(cli, "generate")
        assert os.path.exists("cfn-cli.yaml")

        with patch.object(Context, "runner") as mock_command_runner:

            result = cli_runner.invoke(cli, "validate")
            assert result.exit_code == 0
