# -*- encoding: utf-8 -*-

import os
import pytest
import jsonschema
import shutil
from awscfncli import config


@pytest.fixture
def data_dir(tmpdir):
    data_dir = 'data'
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
        assert 'staging' in environments

        stacks = c.list_stacks('staging')
        assert len(stacks) == 2
        assert 'vpc1' in stacks
        assert 'vpc2' in stacks

        stack = c.get_stack('staging', 'vpc1')
        assert stack['template-body'] == 'default.template'
        assert stack['tags']['key1'] == 'value1'
        assert stack['tags']['key2'] == 'value2'

        stack = c.get_stack('staging', 'vpc2')
        assert stack['template-body'] == 'default.template'
        assert stack['tags']['key3'] == 'value3'
        assert stack['tags']['key4'] == 'value4'

    def test_load_config_with_reused_parameters(self, data_dir):
        configfile = data_dir.join('tests/config_with_reused_parameters.yaml')

        c = config.load_config(configfile)
        assert c is not None

        assert c.version == 2

        environments = c.list_environments()
        assert len(environments) == 1
        assert 'staging' in environments

        stacks = c.list_stacks('staging')
        assert len(stacks) == 3
        assert 'vpc1' in stacks
        assert 'vpc2' in stacks
        assert 'vpc3' in stacks

        stack = c.get_stack('staging', 'vpc1')
        assert stack['template-body'] == 'default.template'
        assert stack['tags']['key1'] == 'value1'
        assert stack['tags']['key2'] == 'value2'

        stack = c.get_stack('staging', 'vpc2')
        assert stack['template-body'] == 'default.template'
        assert 'key1' not in stack['tags']
        assert 'key2' not in stack['tags']
        assert stack['tags']['key3'] == 'value3'
        assert stack['tags']['key4'] == 'value4'

        stack = c.get_stack('staging', 'vpc3')
        assert stack['template-body'] == 'default.template'
        assert stack['tags']['key1'] == 'value1_overide'
        assert stack['tags']['key2'] == 'value2'
