# -*- encoding: utf-8 -*-

import pytest
from awscfncli import config


class TestConfig(object):
    def test_load(self):
        c = config.load('')
        assert c is not None

    def test_validation(self):
        c = config.load('')
        assert c.validate() == False
