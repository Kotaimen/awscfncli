# -*- encoding: utf-8 -*-

import fnmatch
import six
import boto3


class ContextObject(object):
    """Click context object """

    def __init__(self, config,
                 profile,
                 region,
                 verbosity):
        self.config = config
        self.profile = profile
        self.region = region
        self.verbosity = verbosity

    def find_stack_config(self, env_pattern, stack_pattern):
        """ Find matching stack configurations

        Assuming config is a dict of dict of namedtuples:
            config[env][stack] = stack_config

        """
        for env_name in self.config.list_environments():
            if fnmatch.fnmatchcase(env_name, env_pattern):
                for stack_name in self.config.list_stacks(env_name):
                    if fnmatch.fnmatchcase(stack_name, stack_pattern):
                        stack_config = self.config.get_stack(env_name, stack_name)

                        override = dict()

                        # override stack parameters
                        if self.profile is not None:
                            override['profile'] = self.profile
                        if self.region is not None:
                            override['region'] = self.region

                        # clone a new config with new value
                        yield stack_config._replace(**override)

    def find_one_stack_config(self, env_pattern, stack_pattern):
        for stack_config in self.find_stack_config(env_pattern, stack_pattern):
            return stack_config
        else:
            raise RuntimeError('Stack not found.')

    def get_boto3_session(self, stack_config):

        session = boto3.session(
            profile_name=stack_config.profile,
            region_name=stack_config.region
        )

        return session
