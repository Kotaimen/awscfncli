import os
from unittest.mock import patch

import click.testing

from awscfncli2.cli.context import Context
from awscfncli2.cli.main import cli
from awscfncli2.runner.commands.stack_deploy_command import StackDeployCommand
from awscfncli2.runner.commands.stack_delete_command import StackDeleteCommand
from awscfncli2.runner.commands.stack_status_command import StackStatusCommand
from awscfncli2.runner.commands.stack_sync_command import StackSyncCommand
from awscfncli2.runner.commands.stack_update_command import StackUpdateCommand


@patch.object(Context, 'runner')
def test_stack_deploy_command(mock_command_runner):
    cli_runner = click.testing.CliRunner()

    with cli_runner.isolated_filesystem():
        # generate a default config file
        result = cli_runner.invoke(cli, 'generate')
        assert os.path.exists('cfn-cli.yaml')
        assert result.exit_code == 0

        result = cli_runner.invoke(cli, 'stack deploy')
        assert result.exit_code == 0

        command_invoked = mock_command_runner.run.call_args[0][0]
        assert isinstance(command_invoked, StackDeployCommand)


@patch.object(Context, 'runner')
def test_stack_update_command(mock_command_runner):
    cli_runner = click.testing.CliRunner()

    with cli_runner.isolated_filesystem():
        # generate a default config file
        result = cli_runner.invoke(cli, 'generate')
        assert os.path.exists('cfn-cli.yaml')
        assert result.exit_code == 0

        result = cli_runner.invoke(cli, 'stack update')
        assert result.exit_code == 0

        command_invoked = mock_command_runner.run.call_args[0][0]
        assert isinstance(command_invoked, StackUpdateCommand)


@patch.object(Context, 'runner')
def test_stack_status_command(mock_command_runner):
    cli_runner = click.testing.CliRunner()

    with cli_runner.isolated_filesystem():
        # generate a default config file
        result = cli_runner.invoke(cli, 'generate')
        assert os.path.exists('cfn-cli.yaml')
        assert result.exit_code == 0

        result = cli_runner.invoke(cli, 'status')
        assert result.exit_code == 0

        command_invoked = mock_command_runner.run.call_args[0][0]
        assert isinstance(command_invoked, StackStatusCommand)


@patch.object(Context, 'runner')
def test_stack_sync_command(mock_command_runner):
    cli_runner = click.testing.CliRunner()

    with cli_runner.isolated_filesystem():
        # generate a default config file
        result = cli_runner.invoke(cli, 'generate')
        assert os.path.exists('cfn-cli.yaml')
        assert result.exit_code == 0

        result = cli_runner.invoke(cli, 'stack sync')
        assert result.exit_code == 0

        command_invoked = mock_command_runner.run.call_args[0][0]
        assert isinstance(command_invoked, StackSyncCommand)


@patch.object(Context, 'runner')
def test_stack_delete_command(mock_command_runner):
    cli_runner = click.testing.CliRunner()

    with cli_runner.isolated_filesystem():
        # generate a default config file
        result = cli_runner.invoke(cli, 'generate')
        assert os.path.exists('cfn-cli.yaml')
        assert result.exit_code == 0

        result = cli_runner.invoke(cli, 'stack delete')
        assert result.exit_code == 0

        command_invoked = mock_command_runner.run.call_args[0][0]
        assert isinstance(command_invoked, StackDeleteCommand)
