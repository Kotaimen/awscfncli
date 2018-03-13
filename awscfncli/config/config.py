# -*- encoding: utf-8 -*-

import logging
import yaml
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

                stacks[stack_name] = stack_config

            environments[env_name] = stacks

        return environments
