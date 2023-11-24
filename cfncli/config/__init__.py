# -*- encoding: utf-8 -*-
import os.path
from typing import Optional

from .config import load_config, ConfigError
from .deployment import StackKey, StackDeployment
from .formats import CANNED_STACK_POLICIES


with open(os.path.join(os.path.dirname(__file__),
                       'annotated-sample-config.yaml')) as fp:
    ANNOTATED_SAMPLE_CONFIG = fp.read()

with open(os.path.join(os.path.dirname(__file__),
                       'sample-config.yaml')) as fp:
    SAMPLE_CONFIG = fp.read()

DEFAULT_CONFIG_FILE_NAMES = ['cfn-cli.yaml', 'cfn-cli.yml']


def find_default_config(config_filename: Optional[str] = None) -> Optional[str]:
    """Locate default configuration file"""
    if config_filename is None:
        # no config file is specified, try default names
        for fn in DEFAULT_CONFIG_FILE_NAMES:
            config_filename = fn
            if os.path.exists(config_filename) and os.path.isfile(config_filename):
                break
    elif os.path.isdir(config_filename):
        # specified a directory, try default names under given dir
        base = config_filename
        for fn in DEFAULT_CONFIG_FILE_NAMES:
            config_filename = os.path.join(base, fn)
            if os.path.exists(config_filename) and os.path.isfile(config_filename):
                break
    return config_filename
