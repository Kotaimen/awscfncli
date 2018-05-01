# -*- encoding: utf-8 -*-

import logging
import copy
import os
from collections import OrderedDict

import boto3

from ...config import load_config, ConfigError


class ContextObject(object):
    """Click context object"""

    def __init__(self,
                 config_file,
                 stack_selector,
                 profile,
                 region,
                 first_stack,
                 verbosity):

        split = stack_selector.rsplit('.', 1)

        if len(split) == 1:
            stage_pattern = '*'
            stack_pattern = stack_selector
        else:
            stage_pattern = split[0]
            stack_pattern = split[1]

        logging.debug('Stack selector: %s -> %s.%s' % (
            stack_selector, stage_pattern, stack_pattern))

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
        """Config object (lazy loading)"""

        # Layout:
        #
        #     Config {
        #         Stages {
        #             Stacks {
        #                 StackConfig {
        #                     Stack Parameter
        #                     ...
        #                     Metadata {
        #                         Stack Metadata
        #                         ...
        #                     }
        #                 }
        #             }
        #         }
        #     }
        if self._config is None:
            self.load_config()
        return self._config

    @property
    def stacks(self):
        """Stack configs matching the selector"""
        if self._stacks is None:
            self.find_stacks()
        return self._stacks

    def load_config(self):
        """Load config using given context"""

        if not os.path.exists(self.config_file):
            raise ConfigError(
                'Stack config file not found: "{}", specify a valid one '
                'using "-f" option.'.format(self.config_file))

        self._config = load_config(self.config_file)

    def find_stacks(self):
        """Find all matching stacks"""
        configs = list(self.config.search_stacks(
            stage_pattern=self.stage_pattern,
            stack_pattern=self.stack_pattern
        ))

        if not configs:
            available_stacks = ', '.join(
                '.'.join([config.stage_id, config.stack_id]) for
                config in self.config.search_stacks()
            )
            raise ConfigError(
                'No stack matching specified pattern "{}.{}", '.format(
                    self.stage_pattern, self.stack_pattern) +
                'possible values are: ' + available_stacks
            )

        self._stacks = OrderedDict()
        for n, config in enumerate(configs):
            if n > 0 and self.first_stack: return
            # make a deep copy as config may be modified in commands
            stage_id = config.stage_id
            stack_id = config.stack_id
            stack_config = config.to_boto3_format()

            # override parameters
            if self.profile is not None:
                stack_config['Metadata']['Profile'] = self.profile
            if self.region is not None:
                stack_config['Metadata']['Region'] = self.region

            qualified_name = '.'.join([stage_id, stack_id])
            self._stacks[qualified_name] = stack_config

    def get_boto3_session(self, stack_config):
        session = boto3.session.Session(
            profile_name=stack_config['Metadata']['Profile'],
            region_name=stack_config['Metadata']['Region'],
        )

        return session
