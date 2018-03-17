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
        shutil.copytree(data_dir, os.path.join(str(tmpdir), 'tests'))
    return tmpdir


class TestConfig(object):
    def test_load_empty_config(self, data_dir):
        configfile = data_dir.join('tests/empty_config.yaml')

        with pytest.raises(jsonschema.ValidationError):
            c = config.load_config(configfile)

    def test_load_config_with_version(self, data_dir):
        configfile = data_dir.join('tests/config_with_version.yaml')

        c = config.load_config(configfile)

    def test_load_config_with_multi_environments(self, data_dir):
        configfile = data_dir.join('tests/config_with_multi_environments.yaml')

        c = config.load_config(configfile)
        assert c is not None

        assert c.version == 2

        environments = c.list_environments()
        assert len(environments) == 1
        assert 'Staging' in environments

        stacks = c.list_stacks('Staging')
        assert len(stacks) == 2
        assert 'Vpc1' in stacks
        assert 'Vpc2' in stacks

        stack = c.get_stack('Staging', 'Vpc1')
        assert stack['Metadata']['Region'] == 'us-east-1'
        assert stack['Metadata']['Profile'] == 'bob'
        assert stack['TemplateBody'] == 'default.template'
        assert stack['Tags'][0]['Key'] == 'key1'
        assert stack['Tags'][0]['Value'] == 'value1'
        assert stack['Tags'][1]['Key'] == 'key2'
        assert stack['Tags'][1]['Value'] == 'value2'

        stack = c.get_stack('Staging', 'Vpc2')
        assert stack['Metadata']['Region'] == 'us-east-2'
        assert stack['Metadata']['Profile'] == 'ray'
        assert stack['TemplateBody'] == 'default.template'
        assert stack['Tags'][0]['Key'] == 'key3'
        assert stack['Tags'][0]['Value'] == 'value3'
        assert stack['Tags'][1]['Key'] == 'key4'
        assert stack['Tags'][1]['Value'] == 'value4'

    def test_load_config_with_reused_parameters(self, data_dir):
        configfile = data_dir.join('tests/config_with_reused_parameters.yaml')

        c = config.load_config(configfile)
        assert c is not None

        assert c.version == 2

        environments = c.list_environments()
        assert len(environments) == 1
        assert 'Staging' in environments

        stacks = c.list_stacks('Staging')
        assert len(stacks) == 3
        assert 'Vpc1' in stacks
        assert 'Vpc2' in stacks
        assert 'Vpc3' in stacks

        stack = c.get_stack('Staging', 'Vpc1')
        assert stack['Metadata']['Region'] == 'us-east-1'
        assert stack['Metadata']['Profile'] == 'bob'
        assert stack['TemplateBody'] == 'default.template'
        assert stack['Tags'][0]['Key'] == 'key1'
        assert stack['Tags'][0]['Value'] == 'value1'
        assert stack['Tags'][1]['Key'] == 'key2'
        assert stack['Tags'][1]['Value'] == 'value2'

        stack = c.get_stack('Staging', 'Vpc2')
        assert stack['Metadata']['Region'] == 'us-east-1'
        assert stack['Metadata']['Profile'] == 'bob'
        assert stack['TemplateBody'] == 'default.template'
        assert len(stack['Tags']) == 2
        assert stack['Tags'][0]['Key'] == 'key3'
        assert stack['Tags'][0]['Value'] == 'value3'
        assert stack['Tags'][1]['Key'] == 'key4'
        assert stack['Tags'][1]['Value'] == 'value4'

        stack = c.get_stack('Staging', 'Vpc3')
        assert stack['Metadata']['Region'] == 'us-east-1'
        assert stack['Metadata']['Profile'] == 'bob'
        assert stack['TemplateBody'] == 'default.template'
        assert len(stack['Tags']) == 2
        assert stack['Tags'][0]['Key'] == 'key1'
        assert stack['Tags'][0]['Value'] == 'value1_overide'
        assert stack['Tags'][1]['Key'] == 'key2'
        assert stack['Tags'][1]['Value'] == 'value2'

