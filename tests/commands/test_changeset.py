# -*- encoding: utf-8 -*-


import mock

from awscfncli import cfn
from click.testing import CliRunner

__author__ = 'ray'
__date__ = '1/14/17'


def test_cfn_changeset_create(tmpdir):
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

        mock_client.return_value.create_change_set.return_value = {
            'Id': 'MockId'
        }

        runner = CliRunner()
        runner.invoke(cfn, ['changeset', 'create', path.strpath, 'change_name'])

        mock_client.return_value.create_change_set.assert_called_with(
            StackName='ExampleStack',
            ChangeSetName='change_name',
            TemplateURL='https://s3.amazonaws.com/example.template',
            ChangeSetType='UPDATE'
        )

        mock_client.return_value.get_waiter.assert_called_once()


def test_cfn_changeset_describe(tmpdir):
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

        mock_client.return_value.describe_change_set.return_value = {
            'ChangeSetName': 'MockName',
            'ExecutionStatus': 'AVAILABLE',
            'Status': 'CREATE_PENDING',
            'Description': 'MockDescription',
            'StatusReason': 'MockStatusReason',
            'Changes': [
                {
                    'ResourceChange': {
                        'Action': 'Add',
                        'LogicalResourceId': 'MockId',
                        'ResourceType': 'EC2',
                        'PhysicalResourceId': 'MockId',
                        'Replacement': False,
                        'Scope': 'MockScope'
                    }
                },
                {
                    'ResourceChange': {
                        'Action': 'Modify',
                        'LogicalResourceId': 'MockId',
                        'ResourceType': 'EC2',
                        'PhysicalResourceId': 'MockId',
                        'Replacement': False,
                        'Scope': 'MockScope'
                    }
                },
                {
                    'ResourceChange': {
                        'Action': 'Delete',
                        'LogicalResourceId': 'MockId',
                        'ResourceType': 'EC2',
                        'PhysicalResourceId': 'MockId',
                        'Replacement': False,
                        'Scope': 'MockScope'
                    }
                }
            ]
        }

        runner = CliRunner()
        runner.invoke(cfn,
                      ['changeset', 'describe', path.strpath, 'change_name'])

        mock_client.return_value.describe_change_set.assert_called_with(
            StackName='ExampleStack',
            ChangeSetName='change_name'
        )


def test_cfn_changeset_execute(tmpdir):
    with mock.patch('boto3.client', return_value=mock.Mock()) as mock_client, \
            mock.patch('boto3.resource',
                       return_value=mock.Mock()) as mock_resource:
        mock_config = \
            """
            Stack:
              Region:               us-east-1
              StackName:            ExampleStack
              TemplateURL:          https://s3.amazonaws.com/example.template
            """

        path = tmpdir.join('config.yml')
        path.write(mock_config)

        mock_stack = mock.Mock()
        mock_stack.stack_status = 'REVIEW_IN_PROGRESS'

        mock_resource.return_value.Stack.return_value = mock_stack

        runner = CliRunner()
        runner.invoke(cfn,
                      ['changeset', 'execute', path.strpath, 'change_name'])

        mock_client.return_value.execute_change_set.assert_called_with(
            StackName='ExampleStack',
            ChangeSetName='change_name'
        )

        mock_client.return_value.get_waiter.assert_called_once()


def test_cfn_changeset_list(tmpdir):
    with mock.patch('boto3.client', return_value=mock.Mock()) as mock_client, \
            mock.patch('boto3.resource',
                       return_value=mock.Mock()) as mock_resource:
        mock_config = \
            """
            Stack:
              Region:               us-east-1
              StackName:            ExampleStack
              TemplateURL:          https://s3.amazonaws.com/example.template
            """

        path = tmpdir.join('config.yml')
        path.write(mock_config)

        mock_stack = mock.Mock()
        mock_stack.stack_id = 'MockId'

        mock_resource.return_value.Stack.return_value = mock_stack
        mock_client.return_value.list_change_sets.return_value = {
            'Summaries': [
                {
                    'ChangeSetName': 'MockName1',
                    'ChangeSetId': 'MockId1',
                    'Description': 'MockDescription',
                    'ExecutionStatus': 'AVAILABLE',
                    'Status': 'CREATE_PENDING',
                    'StatusReason': 'MockStatusReason'
                },
                {
                    'ChangeSetName': 'MockName2',
                    'ChangeSetId': 'MockId2',
                    'Description': 'MockDescription',
                    'ExecutionStatus': 'AVAILABLE',
                    'Status': 'CREATE_PENDING',
                    'StatusReason': 'MockStatusReason'
                }
            ]
        }

        runner = CliRunner()
        runner.invoke(cfn,
                      ['changeset', 'list', path.strpath])

        mock_client.return_value.list_change_sets.assert_called_with(
            StackName=mock_stack.stack_id,
        )
