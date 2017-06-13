# -*- encoding: utf-8 -*-

import six
import yaml

from collections import OrderedDict

__author__ = 'kotaimen'
__date__ = '09/01/2017'


def normalize(v):
    if isinstance(v, bool):
        return 'true' if v else 'false'
    elif isinstance(v, int):
        return str(v)
    else:
        return v


class ConfigError(RuntimeError):
    pass


class StackConfig(object):
    STACK_CONFIG_DEF = {
        'StackName': (six.string_types, True),
        'Region': (six.string_types, True),
        'TemplateBody': (six.string_types, False),
        'TemplateURL': (six.string_types, False),
        'Package': (bool, False),
        'Parameters': (dict, False),
        'DisableRollback': (bool, False),
        'TimeoutInMinutes': (int, False),
        'NotificationARNs': (list, False),
        'Capabilities': (list, False),
        'ResourceTypes': (list, False),
        'RoleARN': (six.string_types, False),
        'OnFailure': (six.string_types, False),
        'StackPolicyBody': (six.string_types, False),
        'StackPolicyURL': (six.string_types, False),
        'Tags': (dict, False),
    }

    def __init__(self, **kwargs):
        self._props = kwargs

    def validate(self):
        # Should have either 'TemplateBody', 'TemplateURL'
        if not any(k in self._props for k in ('TemplateBody', 'TemplateURL')):
            raise ConfigError(
                'Should specify either TemplateBody, TemplateURL.')
        if all(k in self._props for k in ('TemplateBody', 'TemplateURL')):
            raise ConfigError(
                'Should have one of TemplateBody, TemplateURL.')

        # Check type and requirement
        for k, (t, r) in self.STACK_CONFIG_DEF.items():
            v = self._props.get(k)

            if r and not v:
                # if the required key is missing
                raise ConfigError('Missing required property "%s"' % k)

            if v and not isinstance(v, t):
                # if the value type does not match
                raise ConfigError('Type of "%s" should be "%s"' % (k, str(t)))

        # Check unknown properties
        for k in self._props:
            if k not in self.STACK_CONFIG_DEF:
                raise ConfigError('Unknown property name "%s"' % k)

    def to_dict(self):
        self.validate()

        config = dict(self._props)

        # Normalize parameter config
        if 'Parameters' in config:
            params = list(
                {'ParameterKey': k, 'ParameterValue': normalize(v)}
                for k, v in
                six.iteritems(OrderedDict(
                    sorted(six.iteritems(config['Parameters']))))
            )

            config['Parameters'] = params

        # Normalize tag config
        if 'Tags' in config:
            tags = list(
                {'Key': k, 'Value': v}
                for k, v in
                six.iteritems(OrderedDict(
                    sorted(six.iteritems(config['Tags']))))
            )

            config['Tags'] = tags

        return config

    @staticmethod
    def load_from_yaml(stack_config):
        with open(stack_config, 'r') as fp:
            c = yaml.load(fp)

        return StackConfig(**c['Stack'])


def load_stack_config(stack_config):
    config = StackConfig.load_from_yaml(stack_config)

    return config.to_dict()
