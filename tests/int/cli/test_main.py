"""Test main command"""
import click.testing

from awscfncli2.cli.main import cli


def test_main():

    runner = click.testing.CliRunner()

    with runner.isolated_filesystem():
        # by default, print help when invoked with no options
        result = runner.invoke(cli)
        assert result.exit_code == 0
        assert 'AWS CloudFormation CLI' in result.outputA
