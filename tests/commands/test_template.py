# -*- encoding: utf-8 -*-

import mock

from awscfncli import cfn
from click.testing import CliRunner

from .boto_mock import MOCK_CONFIG, MOCK_CONFIG_WITH_BODY, mock_config, mock_config_with_body, mock_cfn_client

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


def test_cfn_template_validate(mock_config, mock_config_with_body, mock_cfn_client):
    with mock.patch('boto3.client') as mock_client:
        mock_client.return_value = mock_cfn_client

        runner = CliRunner()
        runner.invoke(cfn, ['template', 'validate', mock_config])

        mock_cfn_client.validate_template.assert_called_with(
            TemplateURL=MOCK_CONFIG['TemplateURL']
        )

        runner = CliRunner()
        runner.invoke(cfn, ['template', 'validate', mock_config_with_body])

        mock_cfn_client.validate_template.assert_called_with(
            TemplateBody=MOCK_CONFIG_WITH_BODY['TemplateBody']
        )
