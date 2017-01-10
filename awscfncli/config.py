# -*- encoding: utf-8 -*-

import six
import yaml

__author__ = 'kotaimen'
__date__ = '09/01/2017'


class StackConfig(object):
    STACK_CONFIG_DEF = {
        'StackName': (six.string_types, True),
        'TemplateBody': (six.string_types, False),
        'TemplateURL': (six.string_types, False),
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
        'Tags': (dict, False)
    }

    def __init__(self, **kwargs):
        self._props = kwargs

    def validate(self):
        if not any(k in self._props for k in ('TemplateBody', 'TemplateURL')):
            raise KeyError('Should specify either TemplateBody or TemplateURL.')

        if all(k in self._props for k in ('TemplateBody', 'TemplateURL')):
            raise KeyError('Should not have both TemplateBody and TemplateURL.')

        for k, (t, r) in self.STACK_CONFIG_DEF.items():
            v = self._props.get(k)

            if r and not v:
                # if the required key is missing
                raise KeyError('Missing required property %s' % k)

            if v and not isinstance(v, t):
                # if the value type does not match
                raise TypeError('Type of %s should be %s' % (k, str(t)))

    def to_dict(self):
        self.validate()
        return self._props

    @staticmethod
    def load_from_yaml(stack_config):
        with open(stack_config, 'r') as fp:
            c = yaml.load(fp)

        return StackConfig(**c['Stack'])


def load_stack_config(stack_config):
    config = StackConfig.load_from_yaml(stack_config)

    return config.to_dict()
