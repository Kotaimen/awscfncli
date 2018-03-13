# -*- encoding: utf-8 -*-

import logging
import yaml
from collections import namedtuple
from .schema import validate_config


def load_config(filename):
    logging.debug('Loading config "%s"' % filename)
    with open(filename) as fp:
        config = yaml.safe_load(fp)
        if config is None:
            config = dict()

    return CfnCliConfig(config)


class CfnCliConfig(object):
    def __init__(self, config):
        self._version = self._load_version(config)
        validate_config(config, self._version)
        self._environments = self._load_environments(config)

    @property
    def version(self):
        return self._version

    def list_environments(self):
        return self._environments.keys()

    def list_stacks(self, environment_name):
        return self._environments[environment_name].keys()

    def get_stack(self, environment_name, stack_name):
        return self._environments[environment_name][stack_name]

    def _load_version(self, config):
        version = config.get('Version', 1)
        logging.debug('Loading version %s' % version)
        return version

    def _load_environments(self, config):
        environments = dict()

        for env_name, env_config in config['Environments'].items():
            logging.debug('Loading environment "%s"' % env_name)

            stacks = dict()
            for stack_name, stack_config in env_config.items():
                logging.debug('Loading environment "%s" stack "%s"' % (
                    env_name, stack_name))

                stack_config = dict(stack_config)
                if 'StackName' not in stack_config:
                    stack_config['StackName'] = stack_name

                stacks[stack_name] = StackConfig(**stack_config)

            environments[env_name] = stacks

        return environments


class StackConfig(
    namedtuple('StackConfig', 'StackName Profile Region Package '
                              'ArtifactStorage '
                              'TemplateBody TemplateURL Parameters '
                              'DisableRollback RollbackConfiguration '
                              'TimeoutInMinutes NotificationARNs Capabilities '
                              'ResourceTypes RoleARN OnFailure StackPolicyBody '
                              'StackPolicyURL Tags ClientRequestToken '
                              'EnableTerminationProtection')):
    def __new__(cls,
                StackName=None,
                Profile=None,
                Region=None,
                Package=None,
                ArtifactStorage=None,
                TemplateBody=None,
                TemplateURL=None,
                Parameters=None,
                DisableRollback=None,
                RollbackConfiguration=None,
                TimeoutInMinutes=None,
                NotificationARNs=None,
                Capabilities=None,
                ResourceTypes=None,
                RoleARN=None,
                OnFailure=None,
                StackPolicyBody=None,
                StackPolicyURL=None,
                Tags=None,
                ClientRequestToken=None,
                EnableTerminationProtection=None
                ):
        return super(StackConfig, cls).__new__(
            cls,
            StackName=StackName,
            Profile=Profile,
            Region=Region,
            Package=Package,
            ArtifactStorage=ArtifactStorage,
            TemplateBody=TemplateBody,
            TemplateURL=TemplateURL,
            Parameters=Parameters,
            DisableRollback=DisableRollback,
            RollbackConfiguration=RollbackConfiguration,
            TimeoutInMinutes=TimeoutInMinutes,
            NotificationARNs=NotificationARNs,
            Capabilities=Capabilities,
            ResourceTypes=ResourceTypes,
            RoleARN=RoleARN,
            OnFailure=OnFailure,
            StackPolicyBody=StackPolicyBody,
            StackPolicyURL=StackPolicyURL,
            Tags=Tags,
            ClientRequestToken=ClientRequestToken,
            EnableTerminationProtection=EnableTerminationProtection
        )
