# -*- encoding: utf-8 -*-

import mock

from awscfncli import cfn
from click.testing import CliRunner

from .boto_mock import MOCK_CONFIG, mock_config, mock_cfn_client, mock_cfn

__author__ = 'ray'
__date__ = '1/14/17'


def test_cfn_changeset_create(mock_config, mock_cfn_client):
    with mock.patch('boto3.client') as mock_client:
        mock_client.return_value = mock_cfn_client

        runner = CliRunner()
        runner.invoke(cfn, ['changeset', 'create', mock_config, 'change_name'])

        mock_cfn_client.create_change_set.assert_called_with(
            StackName=MOCK_CONFIG['StackName'],
            ChangeSetName='change_name',
            TemplateURL=MOCK_CONFIG['TemplateURL'],
            ChangeSetType='UPDATE'
        )

        mock_client.return_value.get_waiter.assert_called_once()


def test_cfn_changeset_describe(mock_config, mock_cfn_client):
    with mock.patch('boto3.client') as mock_client:
        mock_client.return_value = mock_cfn_client

        runner = CliRunner()
        runner.invoke(cfn,
                      ['changeset', 'describe', mock_config, 'change_name'])

        mock_cfn_client.describe_change_set.assert_called_with(
            StackName=MOCK_CONFIG['StackName'],
            ChangeSetName='change_name'
        )


def test_cfn_changeset_execute(mock_config, mock_cfn, mock_cfn_client):
    with mock.patch('boto3.client') as mock_client, \
            mock.patch('boto3.resource') as mock_resource:
        mock_resource.return_value = mock_cfn
        mock_client.return_value = mock_cfn_client

        runner = CliRunner()
        runner.invoke(cfn,
                      ['changeset', 'execute', mock_config, 'change_name'])

        mock_cfn_client.execute_change_set.assert_called_with(
            StackName=MOCK_CONFIG['StackName'],
            ChangeSetName='change_name'
        )

        mock_cfn_client.get_waiter.assert_called_once()


def test_cfn_changeset_list(mock_config, mock_cfn, mock_cfn_client):
    with mock.patch('boto3.client') as mock_client, \
            mock.patch('boto3.resource') as mock_resource:
        mock_resource.return_value = mock_cfn
        mock_client.return_value = mock_cfn_client

        runner = CliRunner()
        runner.invoke(cfn, ['changeset', 'list', mock_config])

        mock_cfn_client.list_change_sets.assert_called_with(
            StackName=mock_cfn.Stack.return_value.stack_id,
        )
