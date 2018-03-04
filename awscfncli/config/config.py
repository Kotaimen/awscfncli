# -*- encoding: utf-8 -*-

import six
import logging
import yaml
from collections import namedtuple

log = logging.getLogger(__name__)

CFNFILE_V1 = 1
CFNFILE_V2 = 2


def load(filename):
    return Config()


class Config(namedtuple('_Config', '')):
    def validate(self):
        return False