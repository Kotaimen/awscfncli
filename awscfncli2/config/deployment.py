# -*- coding: utf-8 -*-

import fnmatch
import copy
from collections import namedtuple


def _extends(base, **kwargs):
    for k, v in base.items():
        base[k] = kwargs.get(k, v)


class StackDefaults(object):
    STACK_KEY = dict(
        StageKey=None,
        StackKey=None
    )

    STACK_METADATA = dict(
        StackKey=None,
        Order=None,
        Package=None,
        ArtifactStore=None
    )

    STACK_PROFILE = dict(
        Region=None,
        Profile=None
    )

    STACK_PARAMETERS = dict(
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


class StackKey(namedtuple('StackKey', StackDefaults.STACK_KEY)):

    @property
    def qualified_name(self):
        return '.'.join([self.StageKey, self.StackKey])

    @staticmethod
    def from_dict(**params):
        result = copy.deepcopy(StackDefaults.STACK_KEY)
        _extends(result, **params)
        return StackKey(**result)


class StackMetadata(
    namedtuple('StackMetadata', sorted(StackDefaults.STACK_METADATA))):
    @staticmethod
    def from_dict(**params):
        result = copy.deepcopy(StackDefaults.STACK_METADATA)
        _extends(result, **params)
        return StackMetadata(**result)


class StackProfile(
    namedtuple('StackMetadata', sorted(StackDefaults.STACK_PROFILE))):
    @staticmethod
    def from_dict(**params):
        result = copy.deepcopy(StackDefaults.STACK_PROFILE)
        _extends(result, **params)
        return StackProfile(**result)


class StackParameters(
    namedtuple('StackParameters', sorted(StackDefaults.STACK_PARAMETERS))):
    @staticmethod
    def from_dict(**params):
        result = copy.deepcopy(StackDefaults.STACK_PARAMETERS)
        _extends(result, **params)
        return StackParameters(**result)


class StackDeployment(object):

    def __init__(self, stack_key, stack_metadata, stack_profile, stack_params):
        assert isinstance(stack_key, StackKey)
        assert isinstance(stack_metadata, StackMetadata)
        assert isinstance(stack_profile, StackProfile)
        assert isinstance(stack_params, StackParameters)

        self._stack_key = stack_key
        self._metadata = stack_metadata
        self._profile = stack_profile
        self._parameters = stack_params

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
