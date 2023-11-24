# -*- coding: utf-8 -*-

import fnmatch
import copy
from collections import namedtuple
from .template import find_references, substitute_references


def _extends(base, **kwargs):
    for k, v in base.items():
        base[k] = kwargs.get(k, v)


class StackDefaults(object):
    STACK_KEY = dict(
        StageKey=None,
        StackKey=None
    )

    STACK_METADATA = dict(
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


class StackKey(namedtuple('StackKey', sorted(StackDefaults.STACK_KEY))):

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

    def find_references(self):
        # TODO Need refactor to reduce duplicated ParameterTemplate construction
        return find_references(self._asdict())

    def substitute_references(self, **args):
        return substitute_references(self._asdict(), **args)


class StackDeployment(
    namedtuple('StackDeployment', 'stack_key, metadata, profile, parameters')):
    pass


class Deployment(object):

    def __init__(self):
        self._index = dict()

    def add_stack(self, stage_key, stack_key, stack):
        key = (stage_key, stack_key)
        self._index[key] = stack

    def get_stack(self, stage_key, stack_key):
        key = (stage_key, stack_key)
        return self._index.get(key)

    def get_stacks(self, stage_key):
        return list(k1 for (k1, k2) in self._index if k1 == stage_key)

    def query_stacks(self, stage_pattern='*', stack_pattern='*'):
        """Find all stack config matching stage/stack patterns
        """
        result = list()
        for (k1, k2) in self._index:
            if fnmatch.fnmatchcase(k1, stage_pattern) \
                    and fnmatch.fnmatchcase(k2, stack_pattern):
                result.append(self._index[(k1, k2)])

        result.sort(key=lambda stack: stack.metadata.Order)

        return result
