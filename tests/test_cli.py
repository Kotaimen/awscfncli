# -*- encoding: utf-8 -*-

import pkg_resources

from awscfncli import cfn
from click.testing import CliRunner

__author__ = 'ray'
__date__ = '1/13/17'


def test_cli():
    intro = """Usage: cfn [OPTIONS] COMMAND [ARGS]...

  Welcome to the CloudFormation Stack Management Command Line Interface.

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  changeset  CloudFormation ChangeSet commands
  stack      CloudFormation Stack commands
  template   CloudFormation Template commands
"""

    # test command 'cfn'
    runner = CliRunner()
    result = runner.invoke(cfn)
    assert result.exit_code == 0
    assert result.output == intro

    # test command 'cfn --help'
    result = runner.invoke(cfn, ['--help'])
    assert result.exit_code == 0
    assert str(result.output) == intro

    # test command 'cfn --version'
    version = pkg_resources.require('awscfncli')[0].version
    result = runner.invoke(cfn, ['--version'])
    assert result.exit_code == 0
    assert str(result.output) == 'cfn, version %s\n' % version

    # test command 'cfn --help'
    result = runner.invoke(cfn)
    assert result.exit_code == 0
    assert str(result.output) == intro


def test_cfn_stack():
    intro = """Usage: cfn stack [OPTIONS] COMMAND [ARGS]...

  CloudFormation Stack commands

Options:
  --help  Show this message and exit.

Commands:
  delete    Delete the stack specified in the...
  deploy    Deploy a new stack using specified stack...
  describe  Describe stack status, parameter and output \x08...
  tail      Print stack events and waiting for update...
  update    Update the stack specified in the...
"""

    # test command 'cfn stack'
    runner = CliRunner()
    result = runner.invoke(cfn, ['stack'])
    assert result.exit_code == 0
    assert str(result.output) == intro


def test_cfn_template():
    intro = """Usage: cfn template [OPTIONS] COMMAND [ARGS]...

  CloudFormation Template commands

Options:
  --help  Show this message and exit.

Commands:
  validate  Validate template specified in the config.
"""

    # test command 'cfn template'
    runner = CliRunner()
    result = runner.invoke(cfn, ['template'])
    assert result.exit_code == 0
    assert str(result.output) == intro
