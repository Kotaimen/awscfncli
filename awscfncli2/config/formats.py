# -*- coding: utf-8 -*-

import copy
import os

import jsonschema
import six

from .deployment import StackKey, StackDeployment, StackMetadata, StackProfile, \
    StackParameters, Deployment
from .schema import load_schema
from .template import find_references

CANNED_STACK_POLICIES = {
    'ALLOW_ALL': '{"Statement":[{"Effect":"Allow","Action":"Update:*","Principal":"*","Resource":"*"}]}',
    'ALLOW_MODIFY': '{"Statement":[{"Effect":"Allow","Action":["Update:Modify"],"Principal":"*","Resource":"*"}]}',
    'DENY_DELETE': '{"Statement":[{"Effect":"Allow","NotAction":"Update:Delete","Principal":"*","Resource":"*"}]}',
    'DENY_ALL': '{"Statement":[{"Effect":"Deny","Action":"Update:*","Principal":"*","Resource":"*"}]}',
}


class FormatError(Exception):
    pass


def load_format(version):
    if version == 3:
        return FormatV3
    elif version == 2:
        return FormatV2
    elif version == 1 or version is None:
        return FormatV1
    else:
        raise FormatError('Unspported config version {}'.format(version))


class ConfigFormat(object):
    VERSION = None

    def validate(self, config):
        raise NotImplementedError

    def parse(self, config):
        raise NotImplementedError


class FormatV1(ConfigFormat):
    VERSION = '1.0.0'

    def __init__(self, **context):
        self._context = context

    def validate(self, config):
        schema = load_schema(str(self.VERSION))
        jsonschema.validate(config, schema)

    def parse(self, config):
        raise NotImplementedError


class FormatV2(ConfigFormat):
    VERSION = '2.0.0'

    STAGE_CONFIG = dict(
        Order=(six.integer_types, None),
    )

    STACK_CONFIG = dict(
        Order=(six.integer_types, None),
        Profile=(six.string_types, None),
        Region=(six.string_types, None),
        Package=(bool, None),
        ArtifactStore=(six.string_types, None),
        StackName=(six.string_types, None),
        Template=(six.string_types, None),
        Parameters=(dict, None),
        DisableRollback=(bool, None),
        RollbackConfiguration=(dict, None),
        TimeoutInMinutes=(six.integer_types, None),
        NotificationARNs=(six.string_types, None),
        Capabilities=(list, None),
        ResourceTypes=(list, None),
        RoleARN=(six.string_types, None),
        OnFailure=(six.string_types, None),
        StackPolicy=(six.string_types, None),
        Tags=(dict, None),
        ClientRequestToken=(six.string_types, None),
        EnableTerminationProtection=(bool, None)
    )

    def __init__(self, basedir='.'):
        self._basedir = basedir

    def validate(self, config):
        schema = load_schema(str(self.VERSION))
        jsonschema.validate(config, schema)

        if have_parameter_reference_pattern(config):
            raise jsonschema.SchemaError(
                'Do not support parameter reference in config version <= 2')

    def parse(self, config):
        deployment = Deployment()

        blueprints = config.get('Blueprints', dict())

        stage_configs = config.get('Stages', dict())
        for stage_key, stage_config in stage_configs.items():
            for stack_key, stack_config in stage_config.items():
                if stack_key == 'Order':
                    continue

                base = dict()
                blueprint_id = stack_config.get('Extends')
                if blueprint_id:
                    blueprint = blueprints.get(blueprint_id)
                    if not blueprint:
                        raise FormatError(
                            'Blueprint "%s" not found' % blueprint_id)
                    base = copy.deepcopy(blueprint)

                self._extends(base, stack_config)

                stack = self._build_stack(
                    stage_key, stack_key, stage_config, base)

                deployment.add_stack(stage_key, stack_key, stack)

        return deployment

    def _extends(self, config, extends):
        for key, (typ, default) in self.STACK_CONFIG.items():

            # skip unknown parameters
            if key not in extends:
                continue

            # overwrite Capabilities parameter
            if key == 'Capabilities':
                config[key] = copy.deepcopy(extends[key])
            # append list
            elif typ is list:
                if key not in config:
                    config[key] = list(extends[key])
                else:
                    config[key].extend(extends[key])
            # update dict
            elif typ is dict:
                if key not in config:
                    config[key] = dict(extends[key])
                else:
                    config[key].update(extends[key])
            # copy everything else
            else:
                config[key] = copy.deepcopy(extends[key])

        return config

    def _build_stack(self, stage_key, stack_key, stage_config, stack_config):
        # add default order
        stage_order = stage_config.get('Order', 0)
        stack_order = stack_config.get('Order', 0)
        stack_config['Order'] = (stage_order, stack_order)

        # add default name
        if 'StackName' not in stack_config:
            stack_config['StackName'] = stack_key

        # Make relate template path
        template = stack_config.get('Template')
        if template and \
                not (template.startswith('https') and template.startswith(
                    'http')):
            template_path = os.path.realpath(
                os.path.join(self._basedir, template))
            if not os.path.exists(template_path):
                raise FormatError('File Not Found %s' % template_path)
            stack_config['Template'] = template_path

        stack_policy = stack_config.get('StackPolicy')
        if stack_policy and stack_policy not in CANNED_STACK_POLICIES:
            stack_policy_path = os.path.realpath(
                os.path.join(self._basedir, stack_policy))
            if not os.path.exists(stack_policy_path):
                raise FormatError('File Not Found %s' % stack_policy_path)
            stack_config['StackPolicy'] = stack_policy_path

        key = StackKey(StageKey=stage_key, StackKey=stack_key)
        stack_profile = StackProfile.from_dict(**stack_config)
        stack_parameters = StackParameters.from_dict(**stack_config)
        stack_metadata = StackMetadata.from_dict(**stack_config)

        stack = StackDeployment(
            key, stack_metadata, stack_profile, stack_parameters)

        return stack


def have_parameter_reference_pattern(config):
    match = find_references(config)
    return len(match) > 0


class FormatV3(FormatV2):
    VERSION = '3.0.0'

    def validate(self, config):
        schema = load_schema(str(FormatV2.VERSION))  # use same schema as v2
        jsonschema.validate(config, schema)
