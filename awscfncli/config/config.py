# -*- encoding: utf-8 -*-

from collections import namedtuple, OrderedDict

import logging
import yaml
import six

from .schema import validate_config


class ConfigError(RuntimeError):
    pass


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

                stack_config = stack_config.copy()

                stack_config['StackName'] = stack_name
                stack_config['EnvironmentName'] = env_name

                stacks[stack_name] = StackConfig(**stack_config)

            environments[env_name] = stacks

        return environments


CANNED_STACK_POLICIES = {
    'ALLOW_ALL': '{"Statement":[{"Effect":"Allow","Action":"Update:*","Principal":"*","Resource":"*"}]}',
    'ALLOW_MODIFY': '{"Statement":[{"Effect":"Allow","Action":["Update:Modify"],"Principal":"*","Resource":"*"}]}',
    'DENY_DELETE': '{"Statement":[{"Effect":"Allow","NotAction":"Update:Delete","Principal":"*","Resource":"*"}]}',
    'DENY_ALL': '{"Statement":[{"Effect":"Deny","Action":"Update:*","Principal":"*","Resource":"*"}]}',
}


class StackConfig(
    namedtuple('StackConfig',
               '''StackName
                  TemplateBody TemplateURL Parameters  
                  DisableRollback RollbackConfiguration 
                  TimeoutInMinutes NotificationARNs Capabilities 
                  ResourceTypes RoleARN OnFailure 
                  StackPolicyBody StackPolicyURL 
                  Tags ClientRequestToken
                  EnableTerminationProtection
                  Metadata''')):
    def __new__(cls,
                EnvironmentName=None,
                StackName=None,
                Profile=None,
                Region=None,
                Package=None,
                ArtifactStorage=None,
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
                EnableTerminationProtection=None,
                ):
        # move those are not part of create_stack() call to metadata
        metadata = dict(
            EnvironmentName=EnvironmentName,
            Profile=Profile,
            Region=Region,
            Package=Package,
            ArtifactStorage=ArtifactStorage,
        )

        # XXX: magically select template body or template url
        if Template.startswith('https://s3'):
            TemplateURL, TemplateBody = Template, None
        else:
            TemplateURL, TemplateBody = None, Template

        # lookup canned policy
        if StackPolicy is not None:
            StackPolicyBody = CANNED_STACK_POLICIES[StackPolicy]
        else:
            StackPolicyBody = None

        return super(StackConfig, cls).__new__(
            cls,
            StackName=StackName,
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
            StackPolicyURL=None,
            Tags=Tags,
            ClientRequestToken=ClientRequestToken,
            EnableTerminationProtection=EnableTerminationProtection,
            Metadata=metadata
        )

    @staticmethod
    def _normalize_value(v):
        if isinstance(v, bool):
            return 'true' if v else 'false'
        elif isinstance(v, int):
            return str(v)
        else:
            return v

    def _asdict(self):
        """Overwrite _asdict() to format returning dict same as boto3 api
        expecting."""
        config = super(StackConfig, self)._asdict()
        # drop all None and empty list
        config = dict((k, v) for k, v in six.iteritems(config) if v)
        # Normalize parameter config
        if 'Parameters' in config:
            params = list(
                {
                    'ParameterKey': k,
                    'ParameterValue': self._normalize_value(v)
                }
                for k, v in
                six.iteritems(OrderedDict(
                    sorted(six.iteritems(config['Parameters'])))
                )
            )
            config['Parameters'] = params

        # Normalize tag config
        if 'Tags' in config:
            tags = list(
                {'Key': k, 'Value': v}
                for k, v in
                six.iteritems(OrderedDict(
                    sorted(six.iteritems(config['Tags'])))
                )
            )

            config['Tags'] = tags

        return config
