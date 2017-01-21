# -*- encoding: utf-8 -*-

import json
import mock
import pytest
import datetime

__author__ = 'ray'
__date__ = '1/15/17'


@pytest.fixture(scope='function')
def mock_config_with_templateurl(tmpdir):
    config = \
        """
        Stack:
          Region:               us-east-1
          StackName:            ExampleStack
          TemplateURL:          https://s3.amazonaws.com/example.template
        """

    path = tmpdir.join('config1.yml')
    path.write(config)

    return path.strpath


@pytest.fixture(scope='function')
def mock_config_with_templatebody(tmpdir):
    path = tmpdir.join('example.template')
    path.write(json.dumps({
        'Resource': {}
    }))

    config = \
        """
        Stack:
          Region:               us-east-1
          StackName:            ExampleStack
          TemplateBody:         %s
        """ % path.strpath

    path = tmpdir.join('config2.yml')
    path.write(config)

    return path.strpath


@pytest.fixture(scope='function')
def mock_cfn():
    mock_events_methods = {
        'all.return_value': (
            mock.Mock(
                event_id='MockEventId',
                timestamp=datetime.datetime(2000, 1, 1),
                resource_status='CREATE_COMPLETE',
                logical_resource_id='MockResourceId',
                resource_type='EC2',
                resource_status_reason='',
                physical_resource_id='MockPhysicalResourceId'
            ),
            mock.Mock(
                event_id='MockEventId',
                timestamp=datetime.datetime(2000, 1, 1),
                resource_status='CREATE_IN_PROGRESS',
                logical_resource_id='MockResourceId',
                resource_type='EC2',
                resource_status_reason='MockResourceStatusReason',
                physical_resource_id=''
            )
        ),
    }

    mock_events = mock.Mock(**mock_events_methods)

    mock_stack = mock.Mock(
        stack_id='MockStackId',
        stack_name='ExampleStack',
        description='A Mock Description',
        stack_status='REVIEW_IN_PROGRESS',
        stack_status_reason='A Mock Status Reason',
        parameters=[
            {
                'ParameterKey': 'Param1',
                'ParameterValue': 'Value1'
            }
        ],
        outputs=[
            {
                'OutputKey': 'OutputKey1',
                'OutputValue': 'OutputValue1'
            }
        ],
        tags=[
            {
                'Key': 'TagKey1',
                'Value': 'TagKey1'
            }
        ],
        events=mock_events
    )

    m_attrs = {
        'create_stack.return_value': mock_stack,
        'Stack.return_value': mock_stack
    }
    m = mock.Mock(**m_attrs)

    return m


@pytest.fixture(scope='function')
def mock_cfn_client():
    m_attrs = {
        'get_waiter.return_value': mock.Mock(),
        'create_change_set.return_value': {
            'Id': 'MockId'
        },
        'describe_change_set.return_value': {
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
        },
        'execute_change_set.return_value': {},
        'list_change_sets.return_value': {
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
        },
        'validate_template.return_Value': {}
    }
    m = mock.Mock(**m_attrs)

    return m
