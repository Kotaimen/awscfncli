# -*- encoding: utf-8 -*-

import pytest
import yaml
from awscfncli import config


@pytest.fixture(scope='session')
def dummy_config(tmpdir_factory):
    c = {
        'Version': 2,
        'Blueprints': {},
        'Environments': {}
    }
    fn = tmpdir_factory.mktemp('data').join('img.png')
    with open(fn, 'w') as fp:
        yaml.safe_dump(c, fp)
    return fn


class TestConfig(object):
    def test_load(self, dummy_config):
        c = config.load(dummy_config)
        assert c is not None

        assert c.version == 2
        assert c.blueprints == {}
        assert c.environments == {}
