# -*- encoding: utf-8 -*-

import mock

from awscfncli import cfn
from click.testing import CliRunner

from .boto_mock import mock_config_with_templateurl, mock_cfn_client, mock_cfn

__author__ = 'ray'
__date__ = '1/14/17'


def test_cfn_stack_deploy(
        mock_config_with_templateurl, mock_cfn, mock_cfn_client):
    with mock.patch('boto3.client') as mock_client, \
            mock.patch('boto3.resource') as mock_resource:
        # Mocks
        mock_resource.return_value = mock_cfn
        mock_client.return_value = mock_cfn_client

        runner = CliRunner()
        runner.invoke(cfn, [
            'stack', 'deploy', mock_config_with_templateurl, '--on-failure',
            'ROLLBACK', '--canned-policy', 'DENY_DELETE'])

        mock_resource.assert_called_once_with(
            'cloudformation', region_name='us-east-1')
        mock_cfn.create_stack.assert_called_once()

        mock_client.assert_called_once_with(
            'cloudformation', region_name='us-east-1')
        mock_cfn_client.get_waiter.assert_called_once()


def test_cfn_stack_describe(mock_config_with_templateurl, mock_cfn):
    with mock.patch('boto3.resource') as mock_resource:
        # Mocks
        mock_resource.return_value = mock_cfn

        runner = CliRunner()
        runner.invoke(cfn,
                      ['stack', 'describe', mock_config_with_templateurl, '--stack-resources'])

        mock_resource.assert_called_once_with(
            'cloudformation', region_name='us-east-1')
        mock_cfn.Stack.assert_called_once_with(
            'ExampleStack'
        )


def test_cfn_stack_update(mock_config_with_templateurl, mock_cfn, mock_cfn_client):
    with mock.patch('boto3.client') as mock_client, \
            mock.patch('boto3.resource') as mock_resource:
        # Mocks
        mock_resource.return_value = mock_cfn
        mock_client.return_value = mock_cfn_client

        runner = CliRunner()
        runner.invoke(cfn, ['stack', 'update', mock_config_with_templateurl,
                            '--use-previous-template',
                            '--canned-policy', 'DENY_DELETE',
                            '--override-policy', 'ALLOW_ALL'])

        mock_resource.assert_called_once_with(
            'cloudformation', region_name='us-east-1')
        mock_cfn.Stack.assert_called_once_with(
            'ExampleStack'
        )

        mock_cfn.Stack.return_value.update.assert_called_once_with(
            StackName='ExampleStack',
            UsePreviousTemplate=True,
            StackPolicyBody='''
{
  "Statement" : [
    {
      "Effect" : "Deny",
      "Action" : "Update:Delete",
      "Principal": "*",
      "Resource" : "*"
    }
  ]
}
''',
            StackPolicyDuringUpdateBody='''
{
  "Statement" : [
    {
      "Effect" : "Allow",
      "Action" : "Update:*",
      "Principal": "*",
      "Resource" : "*"
    }
  ]
}
'''
        )

        mock_client.assert_called_once_with(
            'cloudformation', region_name='us-east-1')
        mock_cfn_client.get_waiter.assert_called_once()


def test_cfn_stack_delete(
        mock_config_with_templateurl, mock_cfn, mock_cfn_client):
    with mock.patch('boto3.client') as mock_client, \
            mock.patch('boto3.resource') as mock_resource:
        # Mocks
        mock_resource.return_value = mock_cfn
        mock_client.return_value = mock_cfn_client

        runner = CliRunner()
        runner.invoke(cfn, ['stack', 'delete', mock_config_with_templateurl])

        mock_resource.assert_called_once_with(
            'cloudformation', region_name='us-east-1')
        mock_cfn.Stack.assert_called_once_with(
            'ExampleStack'
        )

        mock_cfn.Stack.return_value.delete.assert_called_once()

        mock_client.assert_called_once_with(
            'cloudformation', region_name='us-east-1')
        mock_cfn_client.get_waiter.assert_called_once()


def test_cfn_stack_tail(mock_config_with_templateurl, mock_cfn):
    with mock.patch('boto3.resource') as mock_resource:
        # Mocks
        mock_resource.return_value = mock_cfn

        runner = CliRunner()
        runner.invoke(cfn, [
            'stack', 'tail', mock_config_with_templateurl, '--timeout', '1'])

        mock_resource.assert_called_once_with(
            'cloudformation', region_name='us-east-1')
        mock_cfn.Stack.assert_called_once_with(
            'ExampleStack'
        )
