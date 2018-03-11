# -*- coding: utf-8 -*-

import os
import json
import jsonschema


def get_schema_path():
    return os.path.dirname(os.path.abspath(__file__))


def load_schema(version):
    filename = os.path.join(
        get_schema_path(), 'schema_v{0}.json'.format(version))
    with open(filename, 'r') as fp:
        return json.load(fp)


def validate_config(config, version):
    schema = load_schema(version)
    jsonschema.validate(config, schema)
