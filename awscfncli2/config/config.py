# -*- coding: utf-8 -*-

import os
import yaml
import logging

from .formats import FormatV1, FormatV2, FormatV21


class ConfigError(Exception):
    pass


class ConfigParser(object):

    def get_format(self, config, **context):
        # inspect version
        version = config.get('Version')
        if version == FormatV21.VERSION:
            return FormatV21(**context)
        elif version == FormatV2.VERSION:
            return FormatV2(**context)
        elif version == FormatV1.VERSION or version is None:
            return FormatV1(**context)
        else:
            raise ConfigError('Unspported config version')

    def parse(self, filename):
        basedir = os.path.dirname(filename)
        with open(filename) as fp:
            config = yaml.safe_load(fp)
            if config is None:
                config = dict()

        fmt = self.get_format(config, basedir=basedir)
        fmt.validate(config)

        deployment = fmt.parse(config)
        return deployment


def load_config(filename):
    logging.debug('Loading config "%s"' % filename)
    try:
        parser = ConfigParser()
        return parser.parse(filename)
    except Exception as e:
        raise ConfigError(e)
