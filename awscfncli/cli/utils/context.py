# -*- encoding: utf-8 -*-

import fnmatch
import copy
import os.path

import boto3

from ...config import load_config, ConfigError


class ContextObject(object):
    """Click context object"""

    def __init__(self,
                 config_file,
                 stage_pattern,
                 stack_pattern,
                 profile,
                 region,
                 first_stack,
                 verbosity):

        self.config_file = config_file
        self.stage_pattern = stage_pattern
        self.stack_pattern = stack_pattern
        self.profile = profile
        self.region = region
        self.first_stack = first_stack
        self.verbosity = verbosity

        # lazy initialization
        self._config = None
        self._stacks = None

    @property
    def config(self):
        """Config object

        Layout:

            Config {
                Stages {
                    Stacks {
                        StackConfig {
                            Stack Parameter
                            ...
                            Metadata {
                                Stack Metadata
                                ...
                            }
                        }
                    }
                }
            }
        """
        if self._config is None:
            self.load_config()
        return self._config

    @property
    def stacks(self):
        """Matching stack configs"""
        if self._stacks is None:
            self.find_stacks()
        return self._stacks

    def load_config(self):
        """Load config using given context"""

        if not os.path.exists(self.config_file):
            raise ConfigError(
                'Stack configuration file not found: "{}", specify a '
                'non-default filename using -f.'.format(self.config_file))
        self._config = load_config(self.config_file)

    def find_stacks(self):
        """Find all matching stacks"""
        stack_configs = list(self._find_stack_config())

        if not stack_configs:
            raise ConfigError(
                'No stack matching specified pattern {}.{}, '.format(
                    self.stage_pattern, self.stack_pattern) +
                'possible values are: \n' +
                '\n'.join(self._find_all_stacks())
            )

        self._stacks = list()
        for n, stack_config in enumerate(stack_configs):
            if n > 0 and self.first_stack: return
            # make a deep copy as config may be modified in commands
            stack_config = copy.deepcopy(stack_config)

            # override parameters
            if self.profile is not None:
                stack_config['Metadata']['Profile'] = self.profile
            if self.region is not None:
                stack_config['Metadata']['Region'] = self.region

            self._stacks.append(stack_config)

    # XXX should be put into config package
    def _find_all_stacks(self):
        for stage_name in self.config.list_environments():
            for stack_name in self.config.list_stacks(stage_name):
                yield '.'.join([stage_name, stack_name])

    # XXX should be put into config package
    def _find_stack_config(self):
        """All stack config matching stage/stack patterns

        """
        for stage_name in self.config.list_environments():
            if fnmatch.fnmatchcase(stage_name, self.stage_pattern):
                for stack_name in self.config.list_stacks(stage_name):
                    if fnmatch.fnmatchcase(stack_name, self.stack_pattern):
                        stack_config = \
                            self.config.get_stack(stage_name, stack_name)
                        yield stack_config

    def get_boto3_session(self, stack_config):

        session = boto3.session.Session(
            profile_name=stack_config['Metadata']['Profile'],
            region_name=stack_config['Metadata']['Region'],
        )

        return session
