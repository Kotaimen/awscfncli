# -*- encoding: utf-8 -*-

import os
import pytest
import shutil
from awscfncli2 import config


@pytest.fixture
def data_dir(tmpdir):
    data_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data')
    if os.path.isdir(data_dir):
        shutil.copytree(data_dir, os.path.join(str(tmpdir), 'data'))
    return tmpdir


class TestConfig(object):

    def test_minium_config(self, data_dir):
        configfile = data_dir.join('data/test.config.minimum.yaml')
        c = config.load_config(configfile)
        assert c is not None

        stack = c.get_stack('Dev', 'Vpc')
        assert 'Vpc' == stack.parameters['StackName']
        assert data_dir.join('data/test.template.yaml') == \
               stack.parameters['Template']

    def test_config_with_stages(self, data_dir):
        configfile = data_dir.join('data/test.config.stages.yaml')
        c = config.load_config(configfile)
        assert c is not None

        stack1 = c.get_stack('Staging', 'Vpc')
        assert stack1 is not None

        stack1 = c.get_stack('Staging1', 'Vpc')
        assert stack1 is not None

        stack1 = c.get_stack('Production', 'Vpc1')
        assert stack1 is not None
        stack1 = c.get_stack('Production', 'Vpc2')
        assert stack1 is not None

    def test_simple_stack_with_stack_name(self, data_dir):
        configfile = data_dir.join('data/test.config.general.yaml')
        c = config.load_config(configfile)

        stack = c.get_stack('Staging', 'Vpc1')

        assert stack.profile['Region'] == 'us-east-1'
        assert stack.profile['Profile'] == 'bob'
        assert stack.parameters['StackName'] == 'StackNameOfVpc1'
        assert stack.parameters['Template'] == data_dir.join('data/test.template.yaml')
        assert stack.parameters['Tags']['key1'] == 'value1'
        assert stack.parameters['Tags']['key2'] == 'value2'

    def test_config_with_extend(self, data_dir):
        configfile = data_dir.join('data/test.config.extends.yaml')
        c = config.load_config(configfile)

        stack = c.get_stack('Staging', 'Vpc0')

        assert stack.profile['Region'] == 'cn-east-1'
        assert stack.profile['Profile'] == 'ray'
        assert stack.parameters['StackName'] == 'Vpc0'
        assert stack.parameters['Template'] == data_dir.join('data/test.template.yaml')
        assert stack.parameters['Capabilities'] == ['CAPABILITY_NAMED_IAM']
        assert stack.parameters['Tags']['Environment'] == 'staging'
        assert stack.parameters['Tags']['Project'] == 'demo'
        assert stack.parameters['Tags']['Test'] == 'test'
        assert len(stack.parameters['Tags']) == 3

        stack = c.get_stack('Staging', 'Vpc1')

        assert stack.profile['Region'] == 'us-east-1'
        assert stack.profile['Profile'] == 'ray'
        assert stack.parameters['StackName'] == 'Vpc1'
        assert stack.parameters['Template'] == data_dir.join('data/test.template.yaml')
        assert stack.parameters['Capabilities'] == ['CAPABILITY_IAM']
        assert stack.parameters['Tags']['Environment'] == 'dev'
        assert stack.parameters['Tags']['Project'] == 'dummy'
        assert len(stack.parameters['Tags']) == 2

        stack = c.get_stack('Prod', 'Vpc0')

        assert stack.profile['Region'] == 'cn-east-1'
        assert stack.profile['Profile'] == 'ray'
        assert stack.parameters['StackName'] == 'Vpc0'
        assert stack.parameters['Template'] == data_dir.join('data/test.template.yaml')
        assert stack.parameters['Capabilities'] == ['CAPABILITY_IAM']
        assert stack.parameters['Tags']['Environment'] == 'prod'
        assert stack.parameters['Tags']['Project'] == 'test'
        assert len(stack.parameters['Tags']) == 2

    def test_query_stacks_with_extends(self, data_dir):
        configfile = data_dir.join('data/test.config.extends.yaml')
        c = config.load_config(configfile)

        stacks = c.query_stacks('*', '*')
        assert len(stacks) == 3
        stack_keys = list(s.stack_key for s in stacks)
        assert ('Prod', 'Vpc0') in stack_keys
        assert ('Staging', 'Vpc0') in stack_keys
        assert ('Staging', 'Vpc1') in stack_keys

        stacks = c.query_stacks('Prod', '*')
        assert len(stacks) == 1
        stack_keys = list(s.stack_key for s in stacks)
        assert ('Prod', 'Vpc0') in stack_keys

        stacks = c.query_stacks('*', 'Vpc1')
        assert len(stacks) == 1
        stack_keys = list(s.stack_key for s in stacks)
        assert ('Staging', 'Vpc1') in stack_keys

    def test_query_stacks(self, data_dir):
        configfile = data_dir.join('data/test.config.stages.yaml')
        c = config.load_config(configfile)

        stacks = c.query_stacks('*', '*')
        assert len(stacks) == 4

