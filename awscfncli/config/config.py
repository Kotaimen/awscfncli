# -*- encoding: utf-8 -*-

import os
import fnmatch
import logging
import yaml
import six
from collections import OrderedDict

from .exceptions import ConfigError
from .schema import validate_config

CANNED_STACK_POLICIES = {
    'ALLOW_ALL': '{"Statement":[{"Effect":"Allow","Action":"Update:*","Principal":"*","Resource":"*"}]}',
    'ALLOW_MODIFY': '{"Statement":[{"Effect":"Allow","Action":["Update:Modify"],"Principal":"*","Resource":"*"}]}',
    'DENY_DELETE': '{"Statement":[{"Effect":"Allow","NotAction":"Update:Delete","Principal":"*","Resource":"*"}]}',
    'DENY_ALL': '{"Statement":[{"Effect":"Deny","Action":"Update:*","Principal":"*","Resource":"*"}]}',
}


def _normalize_value(v):
    if isinstance(v, bool):
        return 'true' if v else 'false'
    elif isinstance(v, int):
        return str(v)
    else:
        return v


def load_config(filename):
    logging.debug('Loading config "%s"' % filename)
    with open(filename) as fp:
        config = yaml.safe_load(fp)
        if config is None:
            config = dict()
    return CfnCliConfig(filename, config)


class CfnCliConfig(object):
    def __init__(self, filename, config):
        self._filename = filename
        self._version = self._load_version(config)
        validate_config(config, self._version)
        self._stages = self._load_stages(config)

    @property
    def version(self):
        return self._version

    def list_stages(self):
        return self._stages.keys()

    def list_stacks(self, stage_name):
        return self._stages[stage_name].keys()

    def get_stack(self, stage_name, stack_name):
        return self._stages[stage_name][stack_name]

    def search_stacks(self, stage_pattern='*', stack_pattern='*'):
        """Find all stack config matching stage/stack patterns
        """
        for stage_name in self.list_stages():
            if fnmatch.fnmatchcase(stage_name, stage_pattern):
                for stack_name in self.list_stacks(stage_name):
                    if fnmatch.fnmatchcase(stack_name, stack_pattern):
                        stack_config = \
                            self.get_stack(stage_name, stack_name)
                        yield stage_name, stack_name, stack_config

    def _load_version(self, config):
        version = config.get('Version', 1)
        logging.debug('Loading version %s' % version)
        return version

    def _load_stages(self, config):
        stages = dict()

        for stage_name, stage_config in config['Stages'].items():
            logging.debug('Loading stage "%s"' % stage_name)

            stacks = dict()
            for stack_name, stack_config in stage_config.items():
                logging.debug('Loading stage "%s" stack "%s"' % (
                    stage_name, stack_name))

                stack_config = stack_config.copy()
                stack_config['StageName'] = stage_name

                if 'StackName' not in stack_config:
                    # if StackName is not specified, use the key of
                    # stack config as stack name.
                    stack_config['StackName'] = stack_name

                stacks[stack_name] = self._create_stack_config(**stack_config)

            stages[stage_name] = stacks

        return stages

    def _create_stack_config(self,
                             StageName=None,
                             StackName=None,
                             Profile=None,
                             Region=None,
                             Package=None,
                             ArtifactStore=None,
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
            StageName=StageName,
            Profile=Profile,
            Region=Region,
            Package=Package,
            ArtifactStore=ArtifactStore,
        )

        # m agically select template body or template url
        if Template.startswith('https') or Template.startswith('http'):
            # s3 template
            TemplateURL, TemplateBody = Template, None
        elif Package:
            # local template with package=on
            TemplateURL = os.path.realpath(
                os.path.join(os.path.dirname(self._filename), Template))
            TemplateBody = None
        else:
            # local template
            TemplateURL = None
            with open(os.path.join(os.path.dirname(self._filename),
                                   Template)) as fp:
                TemplateBody = fp.read()

        # lookup canned policy
        if StackPolicy is not None:
            try:
                StackPolicyBody = CANNED_STACK_POLICIES[StackPolicy]
            except KeyError:
                raise ConfigError('Invalid canned policy "%s", valid values are: %s.' % \
                                  (StackPolicy, ', '.join(CANNED_STACK_POLICIES.keys())))
        else:
            StackPolicyBody = None

        # Normalize parameter config
        normalized_params = None
        if Parameters and isinstance(Parameters, dict):
            normalized_params = list(
                {
                    'ParameterKey': k,
                    'ParameterValue': _normalize_value(v)
                }
                for k, v in
                six.iteritems(OrderedDict(
                    sorted(six.iteritems(Parameters)))
                )
            )

        # Normalize tag config
        normalized_tags = None
        if Tags and isinstance(Tags, dict):
            normalized_tags = list(
                {'Key': k, 'Value': v}
                for k, v in
                six.iteritems(OrderedDict(
                    sorted(six.iteritems(Tags)))
                )
            )

        config = dict(
            Metadata=metadata,
            StackName=StackName,
            TemplateURL=TemplateURL,
            TemplateBody=TemplateBody,
            DisableRollback=DisableRollback,
            RollbackConfiguration=RollbackConfiguration,
            TimeoutInMinutes=TimeoutInMinutes,
            NotificationARNs=NotificationARNs,
            Capabilities=Capabilities,
            ResourceTypes=ResourceTypes,
            RoleARN=RoleARN,
            OnFailure=OnFailure,
            StackPolicyBody=StackPolicyBody,
            Parameters=normalized_params,
            Tags=normalized_tags,
            ClientRequestToken=ClientRequestToken,
            EnableTerminationProtection=EnableTerminationProtection,
        )

        # drop all None and empty list
        config = dict((k, v) for k, v in six.iteritems(config) if v is not None)

        return config
