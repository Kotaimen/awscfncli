from unittest.mock import patch

import click.testing
import pytest

from awscfncli2.cli.context import Context
from awscfncli2.cli.main import cli
from awscfncli2.runner.commands.stack_delete_command import (
    StackDeleteCommand,
    StackDeleteOptions,
)
from awscfncli2.runner.commands.stack_deploy_command import (
    StackDeployCommand,
    StackDeployOptions,
)
from awscfncli2.runner.commands.stack_status_command import (
    StackStatusCommand,
    StackStatusOptions,
)
from awscfncli2.runner.commands.stack_sync_command import (
    StackSyncCommand,
    StackSyncOptions,
)
from awscfncli2.runner.commands.stack_update_command import (
    StackUpdateCommand,
    StackUpdateOptions,
)


@pytest.fixture()
def cli_runner():
    cli_runner = click.testing.CliRunner()
    with cli_runner.isolated_filesystem():
        cli_runner.invoke(cli, "generate")
        yield cli_runner


def test_stack_cancel_command(cli_runner):
    with patch.object(Context, "runner") as mock_command_runner:
        result = cli_runner.invoke(cli, "-f cfn-cli.yaml -s Develop.Table stack cancel")
        assert result.exit_code == 0


def test_stack_delete_command(cli_runner):
    with patch.object(Context, "runner") as mock_command_runner:
        result = cli_runner.invoke(
            cli,
            "-f cfn-cli.yaml -s Develop.Table stack delete "
            "--no-wait --ignore-missing",
        )
        assert result.exit_code == 0

        command_invoked = mock_command_runner.run.call_args[0][0]
        assert isinstance(command_invoked, StackDeleteCommand)

        options_collected = command_invoked.options
        assert isinstance(options_collected, StackDeleteOptions)
        assert options_collected._asdict() == {
            "no_wait": True,
            "ignore_missing": True,
        }


def test_stack_deploy_command(cli_runner):
    with patch.object(Context, "runner") as mock_command_runner:
        result = cli_runner.invoke(
            cli,
            "-f cfn-cli.yaml -s Develop.Table stack deploy "
            "--no-wait --on-failure=DO_NOTHING --disable-rollback "
            "--timeout-in-minutes=88 --ignore-existing",
        )
        assert result.exit_code == 0

        command_invoked = mock_command_runner.run.call_args[0][0]
        assert isinstance(command_invoked, StackDeployCommand)
        options_collected = command_invoked.options

        assert isinstance(options_collected, StackDeployOptions)
        assert options_collected._asdict() == {
            "no_wait": True,
            "on_failure": "DO_NOTHING",
            "disable_rollback": True,
            "timeout_in_minutes": 88,
            "ignore_existing": True,
        }


def test_status_command(cli_runner):
    with patch.object(Context, "runner") as mock_command_runner:
        result = cli_runner.invoke(cli, "-f cfn-cli.yaml -s Develop.Table status -re")

        assert result.exit_code == 0
        command_invoked = mock_command_runner.run.call_args[0][0]

        assert isinstance(command_invoked, StackStatusCommand)

        options_collected = command_invoked.options
        assert isinstance(options_collected, StackStatusOptions)
        assert options_collected._asdict() == {
            "dry_run": False,
            "stack_resources": True,
            "stack_exports": True,
        }


def test_stack_sync_command(cli_runner):
    with patch.object(Context, "runner") as mock_command_runner:
        result = cli_runner.invoke(
            cli,
            "-f cfn-cli.yaml -s Develop.Table stack sync "
            "--no-wait --confirm --use-previous-template",
        )

        assert result.exit_code == 0
        command_invoked = mock_command_runner.run.call_args[0][0]

        assert isinstance(command_invoked, StackSyncCommand)

        options_collected = command_invoked.options
        assert isinstance(options_collected, StackSyncOptions)
        assert options_collected._asdict() == {
            "no_wait": True,
            "confirm": True,
            "use_previous_template": True,
        }


def test_stack_tail_command(cli_runner):
    with patch.object(Context, "runner") as mock_command_runner:
        result = cli_runner.invoke(cli, "-f cfn-cli.yaml -s Develop.Table stack tail")
        assert result.exit_code == 0


def test_stack_update_command(cli_runner):
    with patch.object(Context, "runner") as mock_command_runner:
        result = cli_runner.invoke(
            cli,
            "-f cfn-cli.yaml -s Develop.Table stack update "
            "--no-wait --ignore-no-update --use-previous-template "
            "--override-policy=ALLOW_ALL",
        )
        assert result.exit_code == 0

        command_invoked = mock_command_runner.run.call_args[0][0]
        assert isinstance(command_invoked, StackUpdateCommand)

        options_collected = command_invoked.options
        assert isinstance(options_collected, StackUpdateOptions)
        assert options_collected._asdict() == {
            "no_wait": True,
            "ignore_no_update": True,
            "use_previous_template": True,
            "override_policy": "ALLOW_ALL",
        }
