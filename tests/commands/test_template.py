# -*- encoding: utf-8 -*-

import mock

from awscfncli import cfn
from click.testing import CliRunner

__author__ = 'ray'
__date__ = '1/14/17'


def test_cfn_template_validate_with_error():
    message = """Usage: cfn template validate [OPTIONS] CONFIG_FILE

Error: Missing argument "config_file".
"""

    runner = CliRunner()
    result = runner.invoke(cfn, ['template', 'validate'])
    assert result.exit_code == 2
    assert str(result.output) == message


def test_cfn_template_validate(tmpdir):
    with mock.patch('boto3.client', return_value=mock.Mock()) as mock_client:
        mock_config = \
            """
            Stack:
              Region:               us-east-1
              StackName:            ExampleStack
              TemplateURL:          https://s3.amazonaws.com/example.template
            """

        path = tmpdir.join('config.yml')
        path.write(mock_config)

        runner = CliRunner()
        runner.invoke(cfn, ['template', 'validate', path.strpath])

        mock_client.return_value.validate_template.assert_called_with(
            TemplateURL='https://s3.amazonaws.com/example.template'
        )

        mock_config = \
            """
            Stack:
              Region:               us-east-1
              StackName:            ExampleStack
              TemplateBody:         /example.template
            """

        path = tmpdir.join('config.yml')
        path.write(mock_config)

        runner = CliRunner()
        runner.invoke(cfn, ['template', 'validate', path.strpath])

        mock_client.return_value.validate_template.assert_called_with(
            TemplateBody='/example.template'
        )
