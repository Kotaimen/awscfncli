# -*- encoding: utf-8 -*-

import os
import pytest
import jsonschema
import shutil
from awscfncli import config


@pytest.fixture
def data_dir(tmpdir):
    data_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data')
    if os.path.isdir(data_dir):
        shutil.copytree(data_dir, os.path.join(str(tmpdir), 'data'))
    return tmpdir


class TestConfig(object):
    def test_load_config(self, data_dir):
        configfile = data_dir.join('data/test.config.yaml')
        c = config.load_config(configfile)

        assert c is not None
        assert c.version == 2

    def test_list_stages(self, data_dir):
        configfile = data_dir.join('data/test.config.yaml')
        c = config.load_config(configfile)

        assert c is not None
        assert c.version == 2

        stages = c.list_stages()
        assert len(stages) == 1
        assert 'Staging' in stages

    def test_list_stacks(self, data_dir):
        configfile = data_dir.join('data/test.config.yaml')
        c = config.load_config(configfile)

        assert c is not None
        assert c.version == 2

        stacks = c.list_stacks(stage_name='Staging')
        assert len(stacks) == 3
        assert 'Vpc1' in stacks
        assert 'Vpc2' in stacks
        assert 'Vpc3' in stacks

        stack = c.get_stack('Staging', 'Vpc1')
        assert stack['Metadata']['Region'] == 'us-east-1'
        assert stack['Metadata']['Profile'] == 'bob'
        assert stack['StackName'] == 'StackNameOfVpc1'
        assert stack['TemplateURL'] == data_dir.join('data/test.template.yaml')
        assert stack['Tags'][0]['Key'] == 'key1'
        assert stack['Tags'][0]['Value'] == 'value1'
        assert stack['Tags'][1]['Key'] == 'key2'
        assert stack['Tags'][1]['Value'] == 'value2'

        stack = c.get_stack('Staging', 'Vpc2')
        assert stack['Metadata']['Region'] == 'us-east-2'
        assert stack['Metadata']['Profile'] == 'ray'
        assert stack['StackName'] == 'Vpc2'
        assert stack['TemplateURL'] == data_dir.join('data/test.template.yaml')
        assert stack['Tags'][0]['Key'] == 'key3'
        assert stack['Tags'][0]['Value'] == 'value3'
        assert stack['Tags'][1]['Key'] == 'key4'
        assert stack['Tags'][1]['Value'] == 'value4'

        stack = c.get_stack('Staging', 'Vpc3')
        assert stack['Metadata']['Region'] == 'cn-east-1'
        assert stack['Metadata']['Profile'] == 'ray'
        assert stack['StackName'] == 'Vpc3'
        assert stack['TemplateBody'] == open(data_dir.join('data/test.template.yaml')).read()
        assert stack['Tags'][0]['Key'] == 'Department'
        assert stack['Tags'][0]['Value'] == 'cloud'
        assert stack['Tags'][1]['Key'] == 'Environment'
        assert stack['Tags'][1]['Value'] == 'prod'
        assert stack['Tags'][2]['Key'] == 'Project'
        assert stack['Tags'][2]['Value'] == 'demo'
        assert stack['Capabilities'] == ['CAPABILITY_NAMED_IAM']

