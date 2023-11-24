from unittest.mock import patch

import click.testing
import pytest

from cfncli.cli.context import Context
from cfncli.cli.main import cli
from cfncli.runner.commands.drift_detect_command import (
    DriftDetectCommand,
    DriftDetectOptions,
)
from cfncli.runner.commands.drift_diff_command import (
    DriftDiffCommand,
    DriftDiffOptions,
)


@pytest.fixture()
def cli_runner():
    cli_runner = click.testing.CliRunner()
    with cli_runner.isolated_filesystem():
        cli_runner.invoke(cli, "generate")
        yield cli_runner


def test_drift_detect_command(cli_runner):
    with patch.object(Context, "runner") as mock_command_runner:
        result = cli_runner.invoke(
            cli, "-f cfn-cli.yaml -s Develop.Table drift detect " "--no-wait",
        )
        assert result.exit_code == 0

        command_invoked = mock_command_runner.run.call_args[0][0]
        assert isinstance(command_invoked, DriftDetectCommand)

        options_collected = command_invoked.options
        assert isinstance(options_collected, DriftDetectOptions)
        assert options_collected._asdict() == {
            "no_wait": True,
        }


def test_drift_diff_command(cli_runner):
    with patch.object(Context, "runner") as mock_command_runner:
        result = cli_runner.invoke(cli, "-f cfn-cli.yaml -s Develop.Table drift diff ")
        assert result.exit_code == 0

        command_invoked = mock_command_runner.run.call_args[0][0]
        assert isinstance(command_invoked, DriftDiffCommand)

        options_collected = command_invoked.options
        assert isinstance(options_collected, DriftDiffOptions)
