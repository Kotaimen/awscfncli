# -*- coding: utf-8 -*-

import os
import json
import jsonschema
import string


def get_schema_path():
    return os.path.dirname(os.path.abspath(__file__))


def load_schema(version):
    filename = os.path.join(
        get_schema_path(), 'schema_v{0}.json'.format(version))
    with open(filename, 'r') as fp:
        return json.load(fp)


class ParamReferenceTemplate(string.Template):
    idpattern = r'[_a-z][._a-z0-9-]*'


def have_parameter_reference_pattern(config):
    m = ParamReferenceTemplate.pattern.search(json.dumps(config))
    return m is not None


def validate_schema(config, version):
    schema = load_schema(version)
    jsonschema.validate(config, schema)

    if version <= 2:
        if have_parameter_reference_pattern(config):
            raise jsonschema.SchemaError(
                'Do not support parameter reference in config version <= 2')



