# -*- coding: utf-8 -*-
import os
from cfncli.runner.runbook.package import generate_tempfile


class TestPackage(object):
    def test_generate_temporary_file(self):
        filepath = generate_tempfile()
        print(filepath)
        assert filepath is not None
