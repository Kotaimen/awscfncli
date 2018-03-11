# -*- encoding: utf-8 -*-

import logging
import yaml
from jsonschema import validate

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

CFNCLICONFIG_SCHEMA = {
    "$schema": "http://json-schema.org/schema#",
    'type': 'object',
    'properties': {
        'version': {
            'type': 'integer'
        },
        'blueprints': {
            'type': 'object',
            'additionalProperties': {
                'type': 'object'
            },
        },
        'environments': {
            'type': 'object',
            'additionalProperties': {
                'type': 'object',
                'additionalProperties': {
                    'type': 'object',
                    'properties': {
                        'from': {
                            'type': 'string'
                        },
                        'extends': {
                            'type': 'object'
                        }
                    },
                    'required': ['from']
                }
            }
        }
    },
    'required': ['blueprints', 'environments']

}


def load_config(filename):
    logger.info('Loading config "%s"' % filename)
    with open(filename) as fp:
        config = yaml.safe_load(fp)
    return CfnCliConfig(config)


class CfnCliConfig(object):
    def __init__(self, config):
        validate(config, CFNCLICONFIG_SCHEMA)

        self._version = self._load_version(config)
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
        version = config.get('version', 1)
        logger.debug('Loading version %s' % version)
        return version

    def _load_environments(self, config):
        environments = dict()

        blueprints = config['blueprints']
        for environment_name, environment in config['environments'].items():
            logger.debug('Loading environment "%s"' % environment_name)
            stacks = dict()
            for stack_name, stack in environment.items():
                logger.debug('Loading environment "%s" stack "%s"' % (
                    environment_name, stack_name))

                # copy config from blueprints
                stack_config = dict(blueprints[stack['from']])
                stack_config.update(stack.get('extends'))

                stacks[stack_name] = stack_config

            environments[environment_name] = stacks

        return environments
