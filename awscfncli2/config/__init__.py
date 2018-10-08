# -*- encoding: utf-8 -*-
import os.path

from .config import load_config, ConfigError
from .deployment import StackKey, StackDeployment
from .formats import CANNED_STACK_POLICIES


with open(os.path.join(os.path.dirname(__file__),
                       'annotated-sample-config.yaml')) as fp:
    ANNOTATED_SAMPLE_CONFIG = fp.read()

with open(os.path.join(os.path.dirname(__file__),
                       'sample-config.yaml')) as fp:
    SAMPLE_CONFIG = fp.read()
