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

    @classmethod
    def load(cls, config):
        # load version
        version = config.get(cls.VERSION_SECTION, cls.CFNFILE_V1)

        # load blueprint into dict
        blueprint_section = config.get(cls.BLUEPRINT_SECTION, {})
        blueprints = {}
        for key, val in blueprint_section:
            blueprints[key] = Blueprint.load(val)

        # load environment into dict
        environment_section = config.get(cls.ENVIRONMENT_SECTION, {})
        environments = {}
        for key, val in environment_section:
            environments[key] = Environment.load(val)

        return cls(version, blueprints, environments)


class Stack(namedtuple('Stack', '')):
    @classmethod
    def load(cls, config):
        return cls()


class Environment(namedtuple('Environment', '')):
    @classmethod
    def load(cls, config):
        return cls()


class Blueprint(namedtuple('Blueprint', '')):
    @classmethod
    def load(cls, config):
        return cls()

