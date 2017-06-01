# -*- encoding: utf-8 -*-

import mock

from awscfncli import cfn
from click.testing import CliRunner

from .boto_mock import mock_config_with_templateurl, mock_cfn_client, mock_cfn

__author__ = 'ray'
__date__ = '1/14/17'


def test_cfn_changeset_create(mock_config_with_templateurl, mock_cfn_client):
    with mock.patch('boto3.session.Session') as session:
        # Mocks
        session.return_value.client.return_value = mock_cfn_client

        runner = CliRunner()
        runner.invoke(cfn, [
            'changeset', 'create', mock_config_with_templateurl, 'change_name'])

        mock_cfn_client.create_change_set.assert_called_with(
            StackName='ExampleStack',
            ChangeSetName='change_name',
            TemplateURL='https://s3.amazonaws.com/example.template',
            ChangeSetType='UPDATE'
        )

        mock_cfn_client.get_waiter.assert_called_once()


def test_cfn_changeset_describe(mock_config_with_templateurl, mock_cfn_client):
    with mock.patch('boto3.session.Session') as session:
        # Mocks
        session.return_value.client.return_value = mock_cfn_client

        runner = CliRunner()
        runner.invoke(cfn, [
            'changeset', 'describe', mock_config_with_templateurl,
            'change_name'])

        mock_cfn_client.describe_change_set.assert_called_with(
            StackName='ExampleStack',
            ChangeSetName='change_name'
        )


def test_cfn_changeset_execute(mock_config_with_templateurl, mock_cfn,
                               mock_cfn_client):
    with mock.patch('boto3.session.Session') as session:
        # Mocks
        session.return_value.resource.return_value = mock_cfn
        session.return_value.client.return_value = mock_cfn_client

        runner = CliRunner()
        runner.invoke(cfn, [
            'changeset', 'execute', mock_config_with_templateurl,
            'change_name'])

        mock_cfn_client.execute_change_set.assert_called_with(
            StackName='ExampleStack',
            ChangeSetName='change_name'
        )

        mock_cfn_client.get_waiter.assert_called_once()


def test_cfn_changeset_list(mock_config_with_templateurl, mock_cfn,
                            mock_cfn_client):
    with mock.patch('boto3.session.Session') as session:
        # Mocks
        session.return_value.resource.return_value = mock_cfn
        session.return_value.client.return_value = mock_cfn_client

        runner = CliRunner()
        runner.invoke(cfn, ['changeset', 'list', mock_config_with_templateurl])

        mock_cfn_client.list_change_sets.assert_called_with(
            StackName=mock_cfn.Stack.return_value.stack_id,
        )
