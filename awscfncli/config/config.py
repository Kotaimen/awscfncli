# -*- encoding: utf-8 -*-

import logging
import yaml
from collections import namedtuple

log = logging.getLogger(__name__)


def load_config(filename):
    with open(filename) as fp:
        config = yaml.safe_load(fp)

    return CfnCliConfig.load(config)


class CfnCliConfig(namedtuple('CfnCliConfig', 'version blueprints environments')):
    CFNFILE_V1 = 1
    CFNFILE_V2 = 2

    VERSION_SECTION = 'Version'
    BLUEPRINT_SECTION = 'Blueprints'
    ENVIRONMENT_SECTION = 'Environments'

    @staticmethod
    def load(config):
        # load version
        version = config.get(CfnCliConfig.VERSION_SECTION, CfnCliConfig.CFNFILE_V1)

        # load blueprint into dict
        blueprint_section = config.get(CfnCliConfig.BLUEPRINT_SECTION, {})
        blueprints = {}
        for key, val in blueprint_section:
            blueprints[key] = Blueprint.load(val)

        # load environment into dict
        environment_section = config.get(CfnCliConfig.ENVIRONMENT_SECTION, {})
        environments = {}
        for key, val in environment_section:
            environments[key] = Environment.load(val)

        return CfnCliConfig(version, blueprints, environments)


class Stack(namedtuple('Stack', '')):
    @staticmethod
    def load(config):
        return Stack()


class Environment(namedtuple('Environment', '')):
    @staticmethod
    def load(config):
        return Environment()


class Blueprint(namedtuple('Blueprint', '')):
    @staticmethod
    def load(config):
        return Blueprint()
