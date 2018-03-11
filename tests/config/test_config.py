# -*- encoding: utf-8 -*-

import pytest
import yaml
import jsonschema
from awscfncli import config


@pytest.fixture(scope='session')
def empty_config(tmpdir_factory):
    c = {}
    fn = tmpdir_factory.mktemp('data').join('empty_config.yaml')
    with open(fn, 'w') as fp:
        yaml.safe_dump(c, fp)
    return fn


@pytest.fixture(scope='session')
def dummy_config(tmpdir_factory):
    c = {
        'version': 2,
        'blueprints': {
            'vpc': {
                'template-body': 'default.template',
                'region': 'us-east-1',
                'profile': 'bob',
                'tags': {
                    'key1': 'value1',
                    'key2': 'value2'
                }
            }
        },
        'environments': {
            'staging': {
                'vpc1': {
                    'from': 'vpc',
                    'extends': {
                        'tags': {
                            'key1': 'value1a',
                            'key3': 'value3'
                        }
                    },
                },
                'vpc2': {
                    'from': 'vpc',
                    'extends': {
                        'tags': {
                            'key2': 'value2a',
                            'key4': 'value4'
                        }
                    }
                }
            }
        }
    }
    fn = tmpdir_factory.mktemp('data').join('dummy_config.yaml')
    with open(fn, 'w') as fp:
        yaml.safe_dump(c, fp)
    return fn


class TestConfig(object):
    def test_load_empty_config(self, empty_config):
        with pytest.raises(jsonschema.ValidationError):
            c = config.load_config(empty_config)

    def test_load(self, dummy_config):
        c = config.load_config(dummy_config)
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
        assert stack['tags']['key1'] == 'value1a'
        assert stack['tags']['key3'] == 'value3'
