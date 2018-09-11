# -*- coding: utf-8 -*-

import fnmatch
from collections import OrderedDict, namedtuple


class StackKey(namedtuple('StackKey', ['stage_key', 'stack_key'])):

    @property
    def qualified_name(self):
        return '.'.join([self.stage_key, self.stack_key])


class StackDeployment(object):
    METADATA = dict(
        Key=None,
        Order=None,
        Package=None,
        ArtifactStore=None
    )

    PROFILE = dict(
        Region=None,
        Profile=None
    )

    PARAMETERS = dict(
        StackName=None,
        Template=None,
        Parameters=None,
        DisableRollback=None,
        RollbackConfiguration=None,
        TimeoutInMinutes=None,
        NotificationARNs=None,
        Capabilities=None,
        ResourceTypes=None,
        RoleARN=None,
        OnFailure=None,
        StackPolicy=None,
        Tags=None,
        ClientRequestToken=None,
        EnableTerminationProtection=None
    )

    def __init__(self, stack_key):
        self._stack_key = stack_key
        self._metadata = self.METADATA.copy()
        self._metadata['StackKey'] = stack_key.qualified_name
        self._profile = self.PROFILE.copy()
        self._parameters = self.PARAMETERS.copy()

    @property
    def stack_key(self):
        return self._metadata['StackKey']

    @property
    def metadata(self):
        return self._metadata

    @property
    def profile(self):
        return self._profile

    @property
    def parameters(self):
        return self._parameters

    def update_metadata(self, **kwargs):
        self._update(self._metadata, **kwargs)

    def update_profile(self, **kwargs):
        self._update(self._profile, **kwargs)

    def update_parameters(self, **kwargs):
        self._update(self._parameters, **kwargs)

    def _update(self, properties, **kwargs):
        for k, v in properties.items():
            if k in kwargs:
                properties[k] = kwargs[k]

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, self.stack_key)


class Deployment(object):

    def __init__(self):
        self._index = dict()

    def add_stack(self, stage_key, stack_key, stack):
        key = StackKey(stage_key, stack_key)
        self._index[key] = stack

    def get_stack(self, stage_key, stack_key):
        key = StackKey(stage_key, stack_key)
        return self._index.get(key)

    def get_stacks(self, stage_key):
        return list(k for k in self._index if k.stage_key == stage_key)

    def query_stacks(self, stage_pattern='*', stack_pattern='*'):
        """Find all stack config matching stage/stack patterns
        """
        result = list()
        for key in self._index:
            if fnmatch.fnmatchcase(key.stage_key, stage_pattern) \
                    and fnmatch.fnmatchcase(key.stack_key, stack_pattern):
                result.append(self._index[key])

        result.sort(key=lambda stack: stack.metadata['Order'])

        return result
