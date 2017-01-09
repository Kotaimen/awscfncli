# -*- encoding: utf-8 -*-

import pytest
from awscfncli.config import load_stack_config

__author__ = 'ray'
__date__ = '1/9/17'


def test_load_stack_config(tmpdir):
    mock_config = \
        """
        Stack:
          StackName:            ExampleStack
          TemplateURL:         s3://example/example.template
          Parameters:
            ParameterKey1:      ParameterValue1
            ParameterKey2:      ParameterValue2
          Tags:
            TagKey1:            TagValue1
            TagKey2:            TagValue2
        """

    path = tmpdir.join('config.yml')
    path.write(mock_config)

    expected_value = {
        'StackName': 'ExampleStack',
        'TemplateURL': 's3://example/example.template',
        'Parameters': {
            'ParameterKey1': 'ParameterValue1',
            'ParameterKey2': 'ParameterValue2',
        },
        'Tags': {
            'TagKey1': 'TagValue1',
            'TagKey2': 'TagValue2'
        }
    }

    assert load_stack_config(path.strpath) == expected_value

    path.remove()


def test_load_stack_config_with_error(tmpdir):
    # Missing StackName
    mock_config = \
        """
        Stack:
          TemplateURL:         s3://example/example.template
          Parameters:
            ParameterKey1:      ParameterValue1
            ParameterKey2:      ParameterValue2
          Tags:
            TagKey1:            TagValue1
            TagKey2:            TagValue2
        """
    path = tmpdir.join('config1.yml')
    path.write(mock_config)

    with pytest.raises(KeyError):
        load_stack_config(path.strpath)

    path.remove()

    # Missing TemplateBody or TemplateURL
    mock_config = \
        """
        Stack:
          StackName:            ExampleStack
          Parameters:
            ParameterKey1:      ParameterValue1
            ParameterKey2:      ParameterValue2
          Tags:
            TagKey1:            TagValue1
            TagKey2:            TagValue2
        """
    path = tmpdir.join('config2.yml')
    path.write(mock_config)

    with pytest.raises(KeyError):
        load_stack_config(path.strpath)

    path.remove()

    # Having both TemplateBody and TemplateURL
    mock_config = \
        """
        Stack:
          StackName:            ExampleStack
          TemplateBody:         /example.template
          TemplateURL:          s3://example/example.template
          Parameters:
            ParameterKey1:      ParameterValue1
            ParameterKey2:      ParameterValue2
          Tags:
            TagKey1:            TagValue1
            TagKey2:            TagValue2
        """
    path = tmpdir.join('config2.yml')
    path.write(mock_config)

    with pytest.raises(KeyError):
        load_stack_config(path.strpath)

    path.remove()
